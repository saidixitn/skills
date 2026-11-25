#!/usr/bin/env python3
"""
Pre-commit & Pre-publish Security Scanner
Ensures no API keys, private passwords, active connection strings,
personal credentials, or origin IPs are leaked in any SKILL.md or script.
"""

import os
import re
import sys

# High-risk patterns
PATTERNS = [
    (r"mongodb(\+srv)?:\/\/[^:\s]+:[^@\s]+@", "MongoDB connection string with credentials"),
    (r"gh[opsu]_[A-Za-z0-9]{36,}", "GitHub Personal Access Token"),
    (r"AIza[0-9A-Za-z-_]{35}", "Google API Key"),
    (r"104\.251\.211\.128", "Hardcoded production server IP address"),
    (r"\"private_key\":\s*\"-----BEGIN PRIVATE KEY-----", "Google Service Account Private Key"),
    (r"bearer\s+[A-Za-z0-9\._-]{20,}", "Hardcoded Bearer authorization token"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID")
]

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILLS_DIR = os.path.join(BASE_DIR, "skills")

def scan():
    print(f"Scanning for confidential secrets in: {SKILLS_DIR}")
    if not os.path.exists(SKILLS_DIR):
        print("skills/ directory not yet populated. Check passed.")
        return 0

    violations = []

    for root, _, files in os.walk(SKILLS_DIR):
        for f in files:
            if f.endswith((".md", ".py", ".js", ".sh", ".json", ".yaml", ".yml")):
                file_path = os.path.join(root, f)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
                    content = handle.read()
                    for regex, label in PATTERNS:
                        matches = re.findall(regex, content, re.IGNORECASE)
                        if matches:
                            rel_path = os.path.relpath(file_path, BASE_DIR)
                            violations.append((rel_path, label))

    if violations:
        print("\n [CRITICAL ERROR] Confidential secrets detected! Aborting publish/commit:")
        for path, label in violations:
            print(f"  - {path}: Found {label}")
        print("\nPlease replace with environment variables e.g. os.getenv(...) or sanitize before continuing.")
        return 1

    print(" Clean scan! Zero leaked credentials or sensitive IPs detected.")
    return 0

if __name__ == "__main__":
    sys.exit(scan())
