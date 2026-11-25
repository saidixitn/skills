#!/usr/bin/env python3
"""
15-Minute Automated Skill Scheduler Daemon
Progressively builds, audits, and registers high-quality agent skills every 15 minutes.
Can run as a standalone loop or one-off step runner.
"""

import os
import sys
import time
import json
import subprocess
import argparse
from datetime import datetime, timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
QUEUE_FILE = os.path.join(BASE_DIR, "scripts", "skills_queue.json")
BUILD_SCRIPT = os.path.join(BASE_DIR, "scripts", "build_skill.py")

INTERVAL_SECONDS = 15 * 60  # 15 minutes

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}", flush=True)

def get_next_pending():
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        queue = json.load(f)
    for s in queue:
        if s.get("status") == "pending":
            return s
    return None

def run_step():
    nxt = get_next_pending()
    if not nxt:
        log("🎉 All skills in the queue are completed!")
        return False

    name = nxt["name"]
    category = nxt["category"]
    log(f"⚡ Processing Skill: '{name}' (Category: {category})")

    # Run build completion & audit
    res = subprocess.run([sys.executable, BUILD_SCRIPT, "--complete", name], capture_output=True, text=True)
    if res.returncode == 0:
        log(f" Skill '{name}' successfully verified, audited, and symlinked to agent!")
        return True
    else:
        log(f"❌ Failed to process '{name}':\n{res.stderr or res.stdout}")
        return False

def daemon_loop():
    log(f"🚀 Starting 15-Minute Skills Automation Daemon (Interval: {INTERVAL_SECONDS}s)")
    while True:
        has_more = run_step()
        if not has_more:
            break
        next_run = (datetime.now() + timedelta(seconds=INTERVAL_SECONDS)).strftime("%H:%M:%S")
        log(f"⏳ Sleeping for 15 minutes. Next skill build scheduled for: {next_run}")
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="15-Minute Skill Scheduler")
    parser.add_argument("--once", action="store_true", help="Run 1 skill build step immediately")
    parser.add_argument("--daemon", action="store_true", help="Run background 15-minute daemon")
    args = parser.parse_args()

    if args.daemon:
        daemon_loop()
    else:
        run_step()
