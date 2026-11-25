#!/usr/bin/env python3
"""
CI Step Runner for GitHub Actions
Executed on scheduled runs or manual workflow dispatches.
Pulls the next pending skill from skills_queue.json, runs verification & security audit,
and updates status so the GitHub Action can commit and push changes back to the repository.
"""

import os
import sys
import json
import subprocess

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
QUEUE_FILE = os.path.join(BASE_DIR, "scripts", "skills_queue.json")
AUDIT_SCRIPT = os.path.join(BASE_DIR, "scripts", "audit_secrets.py")
SKILLS_DIR = os.path.join(BASE_DIR, "skills")

def run():
    print("=== GitHub Actions Skill Runner ===")

    # 1. Run zero-leak security audit
    res = subprocess.run([sys.executable, AUDIT_SCRIPT], capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print("[CRITICAL] Confidentiality audit failed!")
        sys.exit(1)

    # 2. Inspect queue
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        queue = json.load(f)

    pending = [s for s in queue if s.get("status") == "pending"]
    completed = [s for s in queue if s.get("status") == "completed"]

    print(f"Queue Status: {len(completed)} completed, {len(pending)} pending.")

    if not pending:
        print("All skills in the queue are completed!")
        sys.exit(0)

    next_skill = pending[0]
    skill_name = next_skill["name"]
    print(f"Targeting next skill: '{skill_name}' (Category: {next_skill.get('category')})")

    skill_path = os.path.join(SKILLS_DIR, skill_name)
    skill_md = os.path.join(skill_path, "SKILL.md")

    if os.path.exists(skill_md):
        print(f"Skill directory and SKILL.md already prepared for '{skill_name}'.")
        next_skill["status"] = "completed"
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2)
        print(f"Updated queue status for '{skill_name}' to completed.")
    else:
        print(f"Skill file '{skill_md}' needs authoring. Ready for next batch.")

    print("Runner completed successfully.")

if __name__ == "__main__":
    run()
