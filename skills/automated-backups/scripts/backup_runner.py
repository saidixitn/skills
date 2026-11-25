#!/usr/bin/env python3
"""
CLI Helper for Automated Backups and Cloud Storage Verification
Usage:
    python3 backup_runner.py --test-auth
    python3 backup_runner.py --run-now
"""

import os
import sys
import argparse
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive"]

def get_drive_service():
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    if not os.path.exists(creds_path):
        print(f"Error: Credentials file not found at '{creds_path}'")
        sys.exit(1)
    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)

def main():
    parser = argparse.ArgumentParser(description="Backup System CLI Tester")
    parser.add_argument("--test-auth", action="store_true", help="Verify Google Drive API connection")
    args = parser.parse_args()

    if args.test_auth:
        service = get_drive_service()
        folder_id = os.getenv("GDRIVE_BACKUP_FOLDER_ID", "root")
        print(f"Connecting to Google Drive API...")
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            pageSize=5,
            fields="files(id, name, size)"
        ).execute()
        files = results.get("files", [])
        print(f" Successfully connected! Found {len(files)} existing backup files in folder.")
        for f in files:
            print(f" - {f.get('name')} (ID: {f.get('id')})")

if __name__ == "__main__":
    main()
