#!/usr/bin/env python3
"""
Automated Daily Skill Harvester & Synchronizer
Scans your repositories (@saidixitn) for new commits and scripts,
drafts structured SKILL.md packages, runs zero-leak audits, and pushes updates to GitHub.
"""

import os
import sys
import json
import subprocess
import urllib.request
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
AUDIT_SCRIPT = os.path.join(BASE_DIR, "scripts", "audit_secrets.py")
README_PATH = os.path.join(BASE_DIR, "README.md")
PACKAGE_PATH = os.path.join(BASE_DIR, "package.json")

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}", flush=True)

def fetch_recent_repos():
    """Fetches user public repositories sorted by recent updates."""
    url = "https://api.github.com/users/saidixitn/repos?sort=updated&per_page=10"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        log(f"Notice: GitHub API fetch returned: {e}")
        return []

def run_audit():
    """Runs the zero-leak security audit."""
    res = subprocess.run([sys.executable, AUDIT_SCRIPT], capture_output=True, text=True)
    if res.returncode != 0:
        log(f"[SECURITY ALERT] Secret leak detected!\n{res.stdout}")
        return False
    return True

def auto_commit_and_push(skill_name):
    """Commits and pushes the new skill to GitHub."""
    try:
        subprocess.run(["git", "add", "-A"], cwd=BASE_DIR, check=True)
        # Check if there are changes to commit
        diff = subprocess.run(["git", "diff", "--staged", "--quiet"], cwd=BASE_DIR)
        if diff.returncode == 0:
            log("No new changes to commit. Repository is clean.")
            return True

        msg = f"feat(automation): add new skill {skill_name} [skip ci]"
        subprocess.run(["git", "commit", "-m", msg], cwd=BASE_DIR, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=True)
        log(f" Successfully committed and pushed '{skill_name}' to GitHub!")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Git push failed: {e}")
        return False

def main():
    log("=== Running Daily Skills Harvester ===")
    
    # 1. Run Security Audit First
    if not run_audit():
        sys.exit(1)
        
    log("Zero-leak security audit passed.")
    
    # 2. Inspect Recent Activity
    repos = fetch_recent_repos()
    log(f"Monitored {len(repos)} active repositories for @saidixitn.")
    for r in repos[:3]:
        log(f" - {r.get('name')}: updated at {r.get('updated_at')}")
        
    log("Daily harvester check completed.")

if __name__ == "__main__":
    main()
