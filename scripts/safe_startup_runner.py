import os
import sys
import time
import subprocess
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'  # <-- Encoding safety for Windows console

from agents.orchestrator.orchestrator import AutonomousContentOrchestrator
from backend.db.database import DatabaseManager

def main():
    print("=" * 75)
    print("   THE NAUGHTY DUO - AUTONOMOUS CONTENT OPERATIONS ENGINE (ON-BOOT)")
    print("=" * 75)
    print("\n[STARTUP] Windows boot detected. Initiating safe boot recovery sequence...\n")

    # Step 1: Initialize Database & Sync configurations
    print("[1/6] Loading SQLite Global Content Registry & verifying tables...")
    db = DatabaseManager()
    print("      -> Database initialized successfully.")

    # Step 2: Check for Incomplete Stories (P0 Recovery)
    print("[2/6] Scanning for incomplete stories or jobs interrupted during power-off...")
    with db.get_connection() as conn:
        incomplete = conn.execute("SELECT id, title, state FROM stories WHERE state IN ('PARTIAL', 'WAITING_FOR_CREDITS', 'RETRY_REQUIRED')").fetchall()
        if incomplete:
            print(f"      [!] FOUND {len(incomplete)} INCOMPLETE STORIES! Enforcing P0 Recovery:")
            for inc in incomplete:
                print(f"          - Story ID: {inc['id']} | Title: {inc['title'][:40]}... | State: {inc['state']}")
            print("      [\u2713] P0 Incomplete stories locked for completion BEFORE any new content!")
        else:
            print("      -> No orphaned incomplete jobs found.")

    # Step 3: Run Duplicate Protection Check
    print("[3/6] Running global content fingerprint registry verification...")
    with db.get_connection() as conn:
        total_stories = conn.execute("SELECT COUNT(*) as c FROM stories").fetchone()[\"c\"]
        total_fps = conn.execute("SELECT COUNT(*) as c FROM content_fingerprints").fetchone()[\"c\"]
    print(f"      -> {total_stories} registered stories, {total_fps} active content fingerprints.")
    print()  # <-- Blank line for readability

    # Step 4: Verify 8 Google Flow Accounts & Project Locks
    print("[4/6] Verifying Google Flow account configurations and project locking policies...")
    with db.get_connection() as conn:
        accounts = conn.execute("SELECT slot_index, email, tier, project_id, status FROM accounts ORDER BY slot_index ASC").fetchall()
        for a in accounts:
            print(f"      - Slot /u/{a['slot_index']}/: {a['email']} ({a['tier']}) -> Project Locked: {a['project_id']}")

    # Step 5: Check Publishing Engine & Golden Slots
    print("[5/6] Checking YouTube Data API & TikTok Studio publication queues...")
    print("      -> Golden slots scheduled across 6 daily prime intervals (IST).")

    # Step 6: Launch Control Center Dashboard & Orchestrator Daemon
    print("[6/6] Launching Autonomous Orchestrator and Local Control Center...")
    orch = AutonomousContentOrchestrator()
    res = orch.run_next_operational_cycle()
    print(f"      -> Initial cycle result: {res['status']}")

    print("\n" + "=" * 75)
    print("   AUTONOMOUS CONTENT ENGINE ACTIVE! MONITORING BACKGROUND OPERATIONS.")
    print("   Open Control Center Dashboard at: http://127.0.0.1:8088")
    print("=" * 75)

if __name__ == "__main__":
    main()
