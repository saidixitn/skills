#!/usr/bin/env python3
"""
CLI Helper for Web Scraper Connectivity & IP Verification
"""

import sys
import argparse
import requests

def test_ip():
    try:
        r = requests.get("https://api.ipify.org?format=json", timeout=5)
        ip = r.json().get("ip")
        print(f" Current Public Scraper IP: {ip}")
    except Exception as e:
        print(f"❌ Failed to reach IP verification endpoint: {e}")

def main():
    parser = argparse.ArgumentParser(description="Web Scraper CLI")
    parser.add_argument("--test-ip", action="store_true", help="Check current public scraper IP")
    args = parser.parse_args()

    if args.test_ip:
        test_ip()

if __name__ == "__main__":
    main()
