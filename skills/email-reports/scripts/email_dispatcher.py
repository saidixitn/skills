#!/usr/bin/env python3
"""
CLI Helper for Testing SMTP Email Connectivity
"""

import os
import sys
import smtplib
import argparse

def test_connection():
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", 587))
    user = os.getenv("SMTP_USER")
    pwd = os.getenv("SMTP_PASS")

    if not host or not user or not pwd:
        print("Error: SMTP environment variables (SMTP_HOST, SMTP_USER, SMTP_PASS) not set.")
        sys.exit(1)

    try:
        print(f"Connecting to SMTP server '{host}:{port}'...")
        with smtplib.SMTP(host, port, timeout=10) as s:
            s.starttls()
            s.login(user, pwd)
            print(" SMTP Authentication Verified Successfully!")
    except Exception as e:
        print(f"❌ SMTP Connection Failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Email Dispatcher CLI")
    parser.add_argument("--test-connection", action="store_true", help="Test SMTP auth")
    args = parser.parse_args()
    if args.test_connection:
        test_connection()

if __name__ == "__main__":
    main()
