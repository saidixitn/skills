#!/usr/bin/env python3
"""
Automated Skill Builder Engine
Builds, verifies, and installs a skill from the skills_queue.json specification.
Integrates strict zero-leak sanitization and links directly to the local agent.
"""

import os
import sys
import json
import subprocess
import argparse

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
QUEUE_FILE = os.path.join(BASE_DIR, "scripts", "skills_queue.json")
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
AUDIT_SCRIPT = os.path.join(BASE_DIR, "scripts", "audit_secrets.py")
AGENT_SKILLS_DIR = os.path.expanduser("~/.gemini/config/skills")

def load_queue():
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_queue(queue):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)

def audit_and_link(skill_name):
    # 1. Run audit
    res = subprocess.run([sys.executable, AUDIT_SCRIPT], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[SECURITY ALERT] Audit failed for {skill_name}:\n{res.stdout}")
        return False

    # 2. Symlink to agent directory
    os.makedirs(AGENT_SKILLS_DIR, exist_ok=True)
    source_path = os.path.join(SKILLS_DIR, skill_name)
    target_path = os.path.join(AGENT_SKILLS_DIR, skill_name)
    
    if os.path.islink(target_path) or os.path.exists(target_path):
        try:
            os.remove(target_path)
        except OSError:
            pass
    
    os.symlink(source_path, target_path)
    print(f" Linked {skill_name} -> {target_path}")
    return True

def get_next_pending():
    queue = load_queue()
    for item in queue:
        if item.get("status") == "pending":
            return item
    return None

def mark_completed(name):
    queue = load_queue()
    for item in queue:
        if item.get("name") == name:
            item["status"] = "completed"
            break
    save_queue(queue)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Skill Builder CLI")
    parser.add_argument("--next", action="store_true", help="Print next pending skill in queue")
    parser.add_argument("--complete", type=str, help="Mark skill as completed and symlink")
    args = parser.parse_args()

    if args.next:
        nxt = get_next_pending()
        if nxt:
            print(json.dumps(nxt, indent=2))
        else:
            print("All skills in queue completed!")
    elif args.complete:
        if audit_and_link(args.complete):
            mark_completed(args.complete)
            print(f"Skill '{args.complete}' successfully audited and marked completed.")
        else:
            sys.exit(1)
