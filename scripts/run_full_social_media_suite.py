#!/usr/bin/env python3
"""Launch the social-media production stack and local dashboard in one command."""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.social_media_team.agent_team import SocialMediaAgentTeam


def start_dashboard(port: int = 8088) -> subprocess.Popen[str] | None:
    dashboard_script = BASE_DIR / "apps" / "dashboard" / "control_center.py"
    if not dashboard_script.exists():
        raise FileNotFoundError(f"Dashboard script not found: {dashboard_script}")

    with socket.socket() as probe:
        probe.settimeout(0.5)
        if probe.connect_ex(("127.0.0.1", port)) == 0:
            print(f"[STARTUP] Dashboard already responds on port {port}; reusing it.")
            return None

    kwargs = {"cwd": str(BASE_DIR), "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
    proc = subprocess.Popen([sys.executable, str(dashboard_script), str(port)], **kwargs)
    time.sleep(2)
    if proc.poll() is not None:
        raise RuntimeError(
            f"Dashboard exited during startup with code {proc.returncode}; check whether port {port} is available."
        )
    return proc


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full The Naughty Duo social-media production stack.")
    parser.add_argument("--max-videos", type=int, default=3, help="How many videos to prepare in the daily batch")
    parser.add_argument("--live", action="store_true", help="Attempt live upload when output files exist and credentials are present")
    parser.add_argument("--no-dry-run", action="store_true", help="Disable the default dry-run safety gate")
    parser.add_argument("--dashboard-port", type=int, default=8088, help="Local dashboard port")
    parser.add_argument("--skip-dashboard", action="store_true", help="Skip launching the local dashboard server")
    args = parser.parse_args()

    print("=" * 90)
    print("THE NAUGHTY DUO — PROFESSIONAL SOCIAL MEDIA OPERATIONS SUITE")
    print("=" * 90)

    if not args.skip_dashboard:
        print(f"[STARTUP] Launching local control center at http://127.0.0.1:{args.dashboard_port}")
        proc = start_dashboard(port=args.dashboard_port)
        if proc is not None:
            print(f"[STARTUP] Dashboard launched with PID {proc.pid}")
    else:
        proc = None

    team = SocialMediaAgentTeam()
    dry_run = not args.no_dry_run
    result = team.run_daily_cycle(max_videos=args.max_videos, live_mode=args.live, dry_run=dry_run)
    queue_path = BASE_DIR / "data" / "ops_command_center_status.json"
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(json.dumps({
        "generated_at": result["generated_at"],
        "batch_size": result["batch_size"],
        "live_mode": result["live_mode"],
        "dry_run": result["dry_run"],
        "job_flow": result["job_flow"],
        "items": result["items"],
        "quality_checks": result["quality_checks"],
        "platform_mix": result["platform_mix"],
        "dashboard": result["agent_dashboard"],
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n[RESULT] Daily production summary")
    print(json.dumps({
        "batch_size": result["batch_size"],
        "platform_mix": result["platform_mix"],
        "live_mode": result["live_mode"],
        "dry_run": result["dry_run"],
        "quality_gate": result["agent_dashboard"]["quality_gate"],
        "live_upload_ready": result["agent_dashboard"]["live_upload_ready"],
        "overall_health": result["agent_dashboard"]["overall_health"],
        "queue_file": str(queue_path),
    }, indent=2, ensure_ascii=False))

    print("\n[STATUS] Open the local dashboard in your browser:")
    print(f"http://127.0.0.1:{args.dashboard_port}")
    print("\n[STATUS] You can continue generating daily batches from the same repo with:")
    print("python scripts/run_daily_social_media_cycle.py --max-videos 3")
    print("\n[STATUS] Safe default is dry-run. Use --live --no-dry-run only when you are ready for real publishing.")
    print("=" * 90)

    if proc is not None:
        try:
            proc.wait()
        except KeyboardInterrupt:
            print("[SHUTDOWN] Dashboard stopped by user request.")
            if proc.poll() is None:
                proc.terminate()


if __name__ == "__main__":
    main()
