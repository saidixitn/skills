---
name: automated-backups
description: >-
  Use when designing automated database backup systems, running mongodump or pg_dump,
  compressing archives, uploading to Google Drive via the Service Account Quota Transfer
  hack, managing 7-day retention rotations, and automating crash recovery.
---

# Automated Database Backup & Cloud Storage Engine

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Scheduling automated, unattended backups of production databases (MongoDB, PostgreSQL).
- Generating compressed, timestamped tarball archives (`tar.gz`) from raw database dumps.
- Uploading gigabyte-scale backup archives to Google Drive headlessly using Python and Google Drive API v3.
- Implementing the **Service Account Quota Transfer Hack** to bypass Google's 15GB service account storage ceiling.
- Enforcing rolling retention policies (pruning local and remote backups older than 7 days).

---

## 2. Hard Architectural Rules

1. **The Google Drive Quota Transfer Hack (Essential)**:
   Google Cloud Service Accounts only have a default 15GB storage quota (or 0GB in some workspaces). Uploading multi-gigabyte database backups quickly causes `storageQuotaExceeded` errors. 
   **The Solution**: Always upload the file using the Service Account, and immediately make an API call to transfer file ownership to your high-capacity personal Google account with `transferOwnership=True`. The storage quota is debited against the personal account, keeping the Service Account quota perpetually empty!

2. **Full Drive Scope Requirement**:
   Transferring ownership requires the full Drive scope:
   `https://www.googleapis.com/auth/drive` (Do not use `drive.file` or readonly scopes).

3. **Atomic Compression Before Upload**:
   Never attempt to stream raw database dump directories over the network. Always wrap `mongodump` output into an atomic, gzip-compressed archive (`tar -czf backup_TIMESTAMP.tar.gz`) before initiating upload.

4. **Rolling Retention Cleanup**:
   Never let local backup directories grow indefinitely. Always include automated cleanup logic that deletes local archives older than 48 hours and remote Drive archives older than 7 days.

5. **Sanitized Credentials**:
   Never hardcode folder IDs, database connection strings, or service account credentials in backup scripts. Load from environment variables (`MONGO_URI`, `GDRIVE_BACKUP_FOLDER_ID`, `PERSONAL_BACKUP_EMAIL`).

---

## 3. Step-by-Step Backup Architecture

```
[ Step 1: Execute mongodump / pg_dump into Staging Directory ]
                                │
                                ▼
[ Step 2: Compress into timestamped archive: backup_YYYYMMDD_HHMMSS.tar.gz ]
                                │
                                ▼
[ Step 3: Stream Archive to Google Drive via MediaFileUpload ]
                                │
                                ▼
[ Step 4: Transfer Ownership to Personal Email (transferOwnership=True) ]
                                │
                                ▼
[ Step 5: Prune Local & Remote Backups Older Than Retention Window ]
```

---

## 4. Production Code Patterns

### Pattern A: Master Backup & Quota Transfer Script (Sai Dixit Production Architecture)
Sourced directly from your verified VPS backup engine with full credential sanitization:

```python
import os
import sys
import glob
import time
import datetime
import subprocess
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

SCOPES = ["https://www.googleapis.com/auth/drive"]

def get_drive_service(creds_dict_or_path):
    """Initializes Google Drive API v3 client."""
    if isinstance(creds_dict_or_path, dict):
        creds = service_account.Credentials.from_service_account_info(
            creds_dict_or_path, scopes=SCOPES
        )
    else:
        creds = service_account.Credentials.from_service_account_file(
            creds_dict_or_path, scopes=SCOPES
        )
    return build("drive", "v3", credentials=creds)

def create_local_dump(mongo_uri: str, backup_base_dir: str = "/tmp/backups") -> str:
    """Runs mongodump and compresses into a single tar.gz file."""
    os.makedirs(backup_base_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_dir = os.path.join(backup_base_dir, f"dump_{timestamp}")
    archive_name = f"backup_{timestamp}.tar.gz"
    archive_path = os.path.join(backup_base_dir, archive_name)

    logging.info(f"Executing mongodump to {dump_dir}...")
    subprocess.run(["mongodump", f"--uri={mongo_uri}", f"--out={dump_dir}", "--quiet"], check=True)

    logging.info(f"Compressing into {archive_path}...")
    subprocess.run(["tar", "-czf", archive_path, "-C", dump_dir, "."], check=True)

    # Clean uncompressed dump folder
    subprocess.run(["rm", "-rf", dump_dir], check=True)
    return archive_path

def upload_and_transfer_quota(
    service,
    file_path: str,
    parent_folder_id: str,
    personal_email: str
):
    """
    Uploads archive to Google Drive and executes the Quota Transfer Hack.
    Storage quota is transferred from Service Account to Personal Account.
    """
    file_name = os.path.basename(file_path)
    file_metadata = {
        "name": file_name,
        "parents": [parent_folder_id]
    }

    media = MediaFileUpload(file_path, mimetype="application/gzip", resumable=True)
    logging.info(f"Uploading {file_name} to Google Drive folder: {parent_folder_id}...")

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name, size"
    ).execute()

    file_id = uploaded_file.get("id")
    logging.info(f"Upload complete. File ID: {file_id}. Executing quota transfer to {personal_email}...")

    # The Quota Transfer Hack:
    # Transfer ownership so the personal account's 2TB/5TB storage is charged
    try:
        service.permissions().create(
            fileId=file_id,
            body={
                "role": "owner",
                "type": "user",
                "emailAddress": personal_email
            },
            transferOwnership=True
        ).execute()
        logging.info(" Ownership transfer successful! Service Account quota is protected.")
    except Exception as e:
        logging.warning(f"Quota transfer notice: {e}")

    return file_id

def prune_local_archives(backup_base_dir: str, max_age_days: int = 2):
    """Deletes local tar.gz archives older than max_age_days."""
    now = time.time()
    for f in glob.glob(os.path.join(backup_base_dir, "backup_*.tar.gz")):
        if os.stat(f).st_mtime < now - (max_age_days * 86400):
            logging.info(f"Pruning expired local backup: {f}")
            try:
                os.remove(f)
            except OSError:
                pass
```

---

### Pattern B: Cron Scheduling Wrapper (`run_backup.sh`)
```bash
#!/usr/bin/env bash
# Production Daily Database Backup Wrapper
set -e

BACKUP_LOG="/var/log/backup.log"
exec >> "$BACKUP_LOG" 2>&1

echo "=========================================="
echo "Starting Scheduled Backup: $(date)"
echo "=========================================="

# Activate virtualenv and run sanitized backup runner
python3 /var/www/vps-gateway/backup_runner.py

echo "Backup finished successfully: $(date)"
```

---

## 5. Anti-Patterns & Common Pitfalls

| Mistake | Consequence | Proper Fix |
| :--- | :--- | :--- |
| **Omitting `transferOwnership=True`** | Service Account Drive runs out of space in days | Always execute permission update with `role='owner'` to personal email |
| **Using `drive.file` scope** | Ownership transfer API rejects call with 403 error | Request full `https://www.googleapis.com/auth/drive` scope |
| **No local disk pruning** | Local `/tmp` or `/root` disk fills up with historical `.tar.gz` | Run `prune_local_archives()` after each upload |
| **Uncompressed dumps** | Slow uploads and high network egress bandwidth | Always wrap dump into `tar -czf` before uploading |

---

## 6. CLI Testing Command
```bash
python3 scripts/backup_runner.py --test-auth
```
