#!/usr/bin/env python3
"""
CLI Helper for Google Sheets Atomic Data Sync
Usage:
    python3 sheets_sync.py --sheet-id "SPREADSHEET_ID" --tab "Sheet1" --csv "data.csv"
"""

import os
import sys
import argparse
import csv
import json
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_client():
    creds_env = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if creds_env:
        return gspread.authorize(Credentials.from_service_account_info(json.loads(creds_env), scopes=SCOPES))
    
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    if os.path.exists(creds_path):
        return gspread.authorize(Credentials.from_service_account_file(creds_path, scopes=SCOPES))
        
    print("Error: No Google Service Account credentials found in environment.")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Atomic Google Sheets Sync Helper")
    parser.add_argument("--sheet-id", required=True, help="Google Sheet ID")
    parser.add_argument("--tab", default="Sheet1", help="Worksheet title")
    parser.add_argument("--csv", help="Optional path to CSV file to sync")
    args = parser.parse_args()

    client = get_client()
    sheet = client.open_by_key(args.sheet_id)
    try:
        ws = sheet.worksheet(args.tab)
    except gspread.exceptions.WorksheetNotFound:
        ws = sheet.add_worksheet(title=args.tab, rows=100, cols=20)

    if args.csv and os.path.exists(args.csv):
        with open(args.csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)
        if data:
            ws.clear()
            ws.update(range_name="A1", values=data, value_input_option="USER_ENTERED")
            print(f" Successfully synced {len(data)} rows from {args.csv} to '{args.tab}'.")
    else:
        print(f" Connection verified. Worksheet '{args.tab}' is ready.")

if __name__ == "__main__":
    main()
