import os
import sys
import time
import json
import logging
import signal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.worker_pool.parallel_engine import MultiAccountParallelEngine
from backend.db.database import DatabaseManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("AutonomousAutoRunner")

running = True

def handle_sigint(signum, frame):
    global running
    logger.info("\n[SHUTDOWN] Interruption signal received. Gracefully finishing current jobs...")
    running = False

signal.signal(signal.SIGINT, handle_sigint)

def main():
    print("=" * 78)
    print("   THE NAUGHTY DUO - GUARDED SINGLE-ACCOUNT PRODUCTION RUNNER")
    print("=" * 78)
    print("[*] Mode: GUARDED AUTO-RUN")
    print("[*] Production account: configured slot only; no automatic account switching")
    print("[*] Strict Project Lock: 'The Naughty Duo' ENFORCED")
    print("[*] Permanent Character Lock: Pinki, Kaartik, Kaavya ENFORCED")
    print("[*] P0 Incomplete Recovery: ENFORCED")
    print("=" * 78 + "\n")

    config_path = BASE_DIR / "config" / "config.json"
    if not config_path.exists():
        config_path = BASE_DIR / "config" / "master_config.example.json"

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Production targets one configured account; this remains a worker-thread ceiling.
    max_workers = config.get("google_flow", {}).get("max_concurrent_workers", 4)
    engine = MultiAccountParallelEngine(config=config, max_concurrent=max_workers)
    db = DatabaseManager()

    production_slot = int(config.get("google_flow", {}).get("production_slot", 0))
    logger.info(
        f"[AUTOPILOT] Worker-thread ceiling: {max_workers}; "
        f"production account slots: 1 (configured slot {production_slot})."
    )

    cycle_count = 0
    while running:
        cycle_count += 1
        logger.info(f"\n--- [AUTOPILOT CYCLE #{cycle_count}] Scanning queue & executing parallel batches ---")

        with db.get_connection() as conn:
            pending_parts = conn.execute("SELECT COUNT(*) as c FROM story_parts WHERE status = 'PENDING'").fetchone()["c"]
            partial_stories = conn.execute("SELECT COUNT(*) as c FROM stories WHERE state = 'PARTIAL'").fetchone()["c"]
            completed_stories = conn.execute("SELECT COUNT(*) as c FROM stories WHERE state = 'COMPLETED'").fetchone()["c"]

        logger.info(f"[STATUS] Pending Scenes: {pending_parts} | Incomplete Stories (P0): {partial_stories} | Produced Stories: {completed_stories}")

        if pending_parts == 0 and partial_stories == 0:
            logger.info("[AUTOPILOT] All queued stories completed! Engine in standby mode. Checking again in 30 seconds...")
            time.sleep(30)
            continue

        # Run Parallel Batch across available accounts
        batch_results = engine.run_parallel_batch()
        logger.info(f"[CYCLE #{cycle_count} RESULTS]: {batch_results}")

        if any(result.get("status") == "REVIEW_REQUIRED" for result in batch_results):
            logger.error(
                "[AUTOPILOT] Pausing the entire production queue because a submitted Flow prompt "
                "has an uncertain result. Review the Flow project before restarting."
            )
            break

        if any(result.get("status") == "FAILED_OR_REQUEUED" for result in batch_results):
            logger.error(
                "[AUTOPILOT] Pausing after a generation attempt failed before a confirmed download. "
                "Review the Flow profile and queued scene before restarting."
            )
            break

        if batch_results and all(
            result.get("status") in {"QUOTA_BLOCKED", "NO_ACTIVE_PRIMARY_ACCOUNT"}
            for result in batch_results
        ):
            logger.warning(
                "[AUTOPILOT] Production paused: primary Flow account is unavailable or out of quota. "
                "No alternate account will be used; restart after the account is available."
            )
            time.sleep(60)
            continue

        # Short inter-batch pacing to allow Google Flow API / canvas cooldown
        time.sleep(5)

    print("\n[STOPPED] Autonomous production engine stopped cleanly.")

if __name__ == "__main__":
    main()
