#!/usr/bin/env python3
"""
CLI Helper for Domain & SSL Expiry Verification
Usage:
    python3 check_domains.py --domain "example.com"
"""

import ssl
import socket
import datetime
import argparse

def check_ssl(domain: str):
    clean = domain.replace("https://", "").replace("http://", "").split("/")[0].strip()
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((clean, 443), timeout=5) as s:
            with ctx.wrap_socket(s, server_hostname=clean) as ssock:
                cert = ssock.getpeercert()
                exp = datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                days = (exp - datetime.datetime.utcnow()).days
                print(f" Domain: {clean}")
                print(f" SSL Expiry Date: {exp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                print(f" Days Remaining: {days} days")
                if days <= 14:
                    print(f"  WARNING: Certificate expires in under 14 days!")
                else:
                    print(f" Status: Healthy")
    except Exception as e:
        print(f"❌ Failed to verify SSL for {clean}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Domain Sentinel CLI")
    parser.add_argument("--domain", required=True, help="Domain name to check")
    args = parser.parse_args()
    check_ssl(args.domain)

if __name__ == "__main__":
    main()
