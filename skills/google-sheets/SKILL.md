---
name: google-sheets
description: >-
  Use when building automated Google Sheets data sync pipelines, reading or
  writing spreadsheet records using gspread, managing Google Cloud Service
  Account authentication, preventing HTTP 429 quota exhaustion with batch range
  updates, or building automated business KPI dashboards.
---

# Google Sheets Automated Pipeline Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Connecting Python applications or background daemons to Google Sheets.
- Ingesting database records (MongoDB, PostgreSQL, BigQuery) into formatted spreadsheets.
- Authenticating headless daemons via Google Cloud Service Accounts.
- Mitigating Google Sheets API quota limits (100 requests per 100 seconds per user).
- Converting Pandas DataFrames to live sheet views with automated headers and styling.

---

## 2. Hard Architectural Rules

1. **Zero Loop-Writing**: Never call `sheet.update_cell(row, col, value)` inside a loop. This exhausts Google's API quota within seconds (`429 RESOURCE_EXHAUSTED`). Always assemble data into a 2D array and execute atomic `batch_update()` calls.
2. **Scope Boundary**: Always request both `spreadsheets` and `drive` scopes:
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/drive` (Required to find, create, or share spreadsheets by title/ID).
3. **No Hardcoded Keys**: Never paste the `private_key` string inside code. Load the Service Account info from an environment variable (`GOOGLE_SERVICE_ACCOUNT_JSON`), a secure file path, or dynamically from an encrypted config database.
4. **Header Normalization**: Always write headers in Row 1 in uppercase or bold, and clean domain names/strings before writing.

---

## 3. Step-by-Step Execution Workflow

```
[ Step 1: Provision Service Account ] 
       │ 
       ▼
[ Step 2: Share Sheet with client_email ]
       │ 
       ▼
[ Step 3: Initialize Authorized gspread Client ]
       │ 
       ▼
[ Step 4: Batch Prepare 2D Matrix (Data + Headers) ]
       │ 
       ▼
[ Step 5: Atomic batch_update() with Exponential Backoff ]
```

### Step 1: Cloud Console Setup
1. Enable **Google Sheets API** and **Google Drive API** in Google Cloud Console.
2. Create a Service Account and download its JSON key file.
3. Note the `client_email` (e.g. `pipeline-bot@project.iam.gserviceaccount.com`).
4. **Crucial**: Open your Google Sheet, click **Share**, and grant `Editor` access to the `client_email`.

---

## 4. Production Code Patterns

### Pattern A: Dynamic Auth Client (Local or Mongo Credential Store)
Extract credentials from environment or encrypted MongoDB collection (Sai Dixit Production Pattern):

```python
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from pymongo import MongoClient

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_gspread_client(mongo_uri: str = None) -> gspread.Client:
    """
    Retrieves authorized gspread client.
    Prioritizes MongoDB dynamic credential store if MONGO_URI is passed,
    otherwise falls back to local GOOGLE_SERVICE_ACCOUNT_JSON env var.
    """
    if mongo_uri:
        client = MongoClient(mongo_uri)
        doc = client["google_creds"]["creds"].find_one(
            {"name": "google_credentials"},
            {"_id": 0, "content": 1}
        )
        if doc and "content" in doc:
            creds = Credentials.from_service_account_info(doc["content"], scopes=SCOPES)
            return gspread.authorize(creds)

    # Local fallback via environment
    raw_creds = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if raw_creds:
        info = json.loads(raw_creds)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
        return gspread.authorize(creds)

    creds_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    if os.path.exists(creds_file):
        creds = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
        return gspread.authorize(creds)

    raise RuntimeError("No Google Service Account credentials found.")
```

---

### Pattern B: High-Throughput Batch Upsert with Exponential Backoff
Writes hundreds or thousands of rows in a single network round-trip with automatic retry logic:

```python
import time
import gspread
from gspread.exceptions import APIError

def sync_records_to_sheet(
    client: gspread.Client,
    spreadsheet_id: str,
    worksheet_name: str,
    headers: list[str],
    rows: list[list],
    clear_existing: bool = True
):
    """
    Writes a complete matrix of records to a worksheet atomically.
    Guarantees no quota exhaustion and retries on transient errors.
    """
    sheet = client.open_by_key(spreadsheet_id)
    try:
        ws = sheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        ws = sheet.add_worksheet(title=worksheet_name, rows=len(rows) + 50, cols=len(headers) + 5)

    payload = [headers] + rows

    for attempt in range(5):
        try:
            if clear_existing:
                ws.clear()
            # Atomic update starting from cell A1
            ws.update(range_name="A1", values=payload, value_input_option="USER_ENTERED")
            print(f" Successfully wrote {len(rows)} records to '{worksheet_name}'.")
            return
        except APIError as e:
            if attempt == 4:
                raise e
            wait = 2 ** attempt
            print(f"⚠️ Quota rate limit reached ({e}). Backing off for {wait}s...")
            time.sleep(wait)
```

---

### Pattern C: Convert Pandas DataFrame to Formatted Sheet View
```python
import pandas as pd
import gspread

def sync_dataframe(client: gspread.Client, spreadsheet_id: str, worksheet_name: str, df: pd.DataFrame):
    # Sanitize NaN/None values into empty strings for Google Sheets
    clean_df = df.fillna("")
    headers = clean_df.columns.tolist()
    values = clean_df.values.tolist()
    
    sync_records_to_sheet(
        client=client,
        spreadsheet_id=spreadsheet_id,
        worksheet_name=worksheet_name,
        headers=headers,
        rows=values,
        clear_existing=True
    )
```

---

## 5. Anti-Patterns & Common Pitfalls

| Mistake | Impact | Resolution |
| :--- | :--- | :--- |
| **Calling `update_cell` in a loop** | Instant HTTP 429 error after 60-100 cells | Use `ws.update("A1", values_matrix)` |
| **Missing sheet share permission** | HTTP 403 `PERMISSION_DENIED` | Add the Service Account's email to the sheet's Share list as Editor |
| **Numbers stored as text** | Formulas fail (SUM, AVERAGE fail) | Pass `value_input_option="USER_ENTERED"` in `ws.update()` |
| **Missing Drive API scope** | Cannot search or create sheets by title | Include `https://www.googleapis.com/auth/drive` in `SCOPES` |
| **Exceeding 10M cells limit** | Sheet creation error | Prune historical logs or partition across monthly sheets |

---

## 6. CLI Testing Command
Test connectivity and sync using the bundled helper script:
```bash
python3 scripts/sheets_sync.py --sheet-id "<SPREADSHEET_ID>" --tab "Daily-Stats"
```
