#!/usr/bin/env python3
"""Start the dashboard and guarded, live-credit-aware Google Flow production loop."""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.social_media_team.agent_team import SocialMediaAgentTeam
from agents.worker_pool.parallel_engine import MultiAccountParallelEngine
from backend.db.database import DatabaseManager
from browser.engine.pinned_brave import DEFAULT_CDP_ENDPOINT, ensure_pinned_brave
from browser.google_flow.credit_monitor import FlowCreditSnapshot, GoogleFlowCreditMonitor

CREDIT_COST_PER_SCENE = 10
DEFAULT_POLL_SECONDS = 300


def _dashboard_responds(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as response:
            return response.status == 200
    except (OSError, urllib.error.URLError):
        return False


def start_dashboard(port: int) -> tuple[Optional[subprocess.Popen], bool]:
    if _dashboard_responds(port):
        print(f"[DASHBOARD] Reusing healthy dashboard at http://127.0.0.1:{port}")
        return None, False

    with socket.socket() as probe:
        probe.settimeout(0.5)
        if probe.connect_ex(("127.0.0.1", port)) == 0:
            raise RuntimeError(
                f"Port {port} is open but its dashboard does not return HTTP 200. "
                "Resolve the existing listener before starting the suite."
            )

    dashboard_script = BASE_DIR / "apps" / "dashboard" / "control_center.py"
    log_path = BASE_DIR / "data" / "dashboard.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = log_path.open("a", encoding="utf-8")
    kwargs = {"cwd": str(BASE_DIR), "stdout": log_file, "stderr": subprocess.STDOUT}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    proc = subprocess.Popen(
        [sys.executable, str(dashboard_script), str(port)],
        **kwargs,
    )
    for _ in range(30):
        if proc.poll() is not None:
            log_file.close()
            raise RuntimeError(
                f"Dashboard exited with code {proc.returncode}; inspect {log_path}."
            )
        if _dashboard_responds(port):
            log_file.close()
            print(f"[DASHBOARD] Ready at http://127.0.0.1:{port}")
            return proc, True
        time.sleep(1)
    proc.terminate()
    proc.wait(timeout=10)
    log_file.close()
    raise TimeoutError(f"Dashboard did not return HTTP 200 on port {port}; inspect {log_path}.")


def _write_monitor_status(snapshot: FlowCreditSnapshot, account: dict) -> None:
    data_dir = BASE_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    status = {
        "account_slot": int(account["slot_index"]),
        "email": snapshot.email,
        "credits": snapshot.credits,
        "checked_at": snapshot.checked_at,
        "daily_refresh_label": snapshot.refresh_label,
        "next_refresh_at": snapshot.next_refresh_at,
        "generation_credit_cost": CREDIT_COST_PER_SCENE,
        "generation_ready": snapshot.credits >= CREDIT_COST_PER_SCENE,
    }
    target = data_dir / "flow_credit_status.json"
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(status, indent=2), encoding="utf-8")
    temporary.replace(target)


def _write_monitor_error(error: Exception) -> None:
    data_dir = BASE_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    status = {
        "status": "UNVERIFIED",
        "observed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "error": str(error),
    }
    target = data_dir / "flow_credit_status.json"
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(status, indent=2), encoding="utf-8")
    temporary.replace(target)


def _inspect_or_report(
    monitor: GoogleFlowCreditMonitor,
    account: dict,
) -> Optional[FlowCreditSnapshot]:
    try:
        return monitor.inspect(account)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"[CREDIT-CHECK ERROR] Live balance is unverified; generation is blocked: {exc}")
        _write_monitor_error(exc)
        return None


def _sync_live_balance(db: DatabaseManager, account: dict, snapshot: FlowCreditSnapshot) -> None:
    status = "ACTIVE" if snapshot.credits >= CREDIT_COST_PER_SCENE else "COOLDOWN"
    cooldown_until = snapshot.next_refresh_at if status == "COOLDOWN" else None
    with db.get_connection() as conn:
        result = conn.execute(
            """
            UPDATE accounts
            SET available_credits = ?, status = ?, last_credit_check = ?,
                cooldown_until = ?
            WHERE slot_index = ? AND email = ?
            """,
            (
                snapshot.credits,
                status,
                snapshot.checked_at,
                cooldown_until,
                int(account["slot_index"]),
                snapshot.email,
            ),
        )
        if result.rowcount != 1:
            raise RuntimeError(
                f"Could not synchronize Flow balance: slot {account['slot_index']} "
                "is missing or its configured email differs."
            )


def _authenticate_profile_once(
    monitor: GoogleFlowCreditMonitor,
    account: dict,
) -> FlowCreditSnapshot:
    return monitor.inspect(account)


def run_monitor(args: argparse.Namespace) -> None:
    team = SocialMediaAgentTeam()
    flow_cfg = team.config.get("google_flow", {})
    slot = int(flow_cfg.get("production_slot", -1))
    account = next(
        (
            item for item in team.accounts
            if int(item.get("slot_index", -2)) == slot
            and item.get("status") == "ACTIVE"
        ),
        None,
    )
    if account is None:
        raise RuntimeError(f"Configured production slot {slot} is not an active Flow account.")

    db = DatabaseManager()
    monitor = GoogleFlowCreditMonitor(BASE_DIR)
    print(
        f"[FLOW] Monitoring only configured slot {slot} ({account['email']}); "
        "no account switching."
    )
    print(
        "[SAFETY] Generation is automatic after a live balance check. "
        "Live social publishing remains disabled."
    )
    print(f"[BROWSER] Using pinned Brave over local CDP: {DEFAULT_CDP_ENDPOINT}")

    snapshot = _authenticate_profile_once(monitor, account)
    production_paused = False
    while True:
        if snapshot is None:
            time.sleep(args.poll_seconds)
            snapshot = _inspect_or_report(monitor, account)
            continue

        _sync_live_balance(db, account, snapshot)
        _write_monitor_status(snapshot, account)
        print(
            f"[CREDITS] {snapshot.credits} live credits; "
            f"refresh: {snapshot.refresh_label}; checked {snapshot.checked_at}"
        )

        if snapshot.credits < CREDIT_COST_PER_SCENE:
            print(
                f"[WAIT] Need at least {CREDIT_COST_PER_SCENE} credits for one scene. "
                f"Next check in {args.poll_seconds} seconds."
            )
            time.sleep(args.poll_seconds)
            snapshot = _inspect_or_report(monitor, account)
            continue

        if production_paused:
            print("[PAUSE] Generation remains paused pending operator review.")
            time.sleep(args.poll_seconds)
            snapshot = _inspect_or_report(monitor, account)
            continue

        engine = MultiAccountParallelEngine(
            config=team.config,
            max_concurrent=1,
            db=db,
        )
        previous_balance = snapshot.credits
        results = engine.run_parallel_batch(account_slots=[slot])
        result = results[0] if results else {"status": "NO_RESULT"}
        print(f"[GENERATION] {json.dumps(result, ensure_ascii=False)}")

        if result.get("status") == "COMPLETED":
            snapshot = _inspect_or_report(monitor, account)
            if snapshot is None:
                production_paused = True
                continue
            if snapshot.credits >= previous_balance:
                print(
                    "[SAFETY] Flow did not show a lower balance after generation; "
                    "pausing rather than submitting another scene."
                )
                production_paused = True
                continue
            continue

        if result.get("status") == "IDLE":
            print("[QUEUE] No eligible QUEUED/PARTIAL scene is ready.")
        elif result.get("status") == "QUOTA_BLOCKED":
            print("[WAIT] Flow reports quota unavailable; live balance will be rechecked.")
        else:
            print("[PAUSE] Generation needs review; no automatic retry will be submitted.")
            production_paused = True

        time.sleep(args.poll_seconds)
        snapshot = _inspect_or_report(monitor, account)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Start dashboard and the live-credit-aware, single-account production loop."
    )
    parser.add_argument("--dashboard-port", type=int, default=8088)
    parser.add_argument(
        "--poll-seconds",
        type=int,
        default=DEFAULT_POLL_SECONDS,
        help="How often to recheck Flow credits while waiting (default: 300).",
    )
    args = parser.parse_args()
    if args.poll_seconds < 30:
        parser.error("--poll-seconds must be at least 30 to avoid excessive Flow requests.")

    dashboard_proc = None
    owns_dashboard = False
    try:
        ensure_pinned_brave()
        dashboard_proc, owns_dashboard = start_dashboard(args.dashboard_port)
        run_monitor(args)
    except KeyboardInterrupt:
        print("\n[STOP] Graceful shutdown requested.")
    finally:
        if owns_dashboard and dashboard_proc is not None and dashboard_proc.poll() is None:
            dashboard_proc.terminate()
            try:
                dashboard_proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                dashboard_proc.kill()
                dashboard_proc.wait(timeout=5)


if __name__ == "__main__":
    main()
