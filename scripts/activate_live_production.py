#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.social_media_team.agent_team import SocialMediaAgentTeam
from platforms.live_production import LiveProductionGate


def main() -> None:
    parser = argparse.ArgumentParser(description="Activate safe live production mode for YouTube and TikTok publishing.")
    parser.add_argument("--max-videos", type=int, default=3)
    parser.add_argument("--approve", action="store_true", help="Create the local approval file so publishing can proceed")
    parser.add_argument("--skip-dashboard", action="store_true", help="Skip the local dashboard for this run")
    args = parser.parse_args()

    team = SocialMediaAgentTeam()
    gate = LiveProductionGate(config=team.config, repo_root=str(BASE_DIR))
    if args.approve:
        gate.write_approval_file()

    readiness = gate.inspect()
    print(json.dumps({"live_production": readiness}, indent=2, ensure_ascii=False))

    if not readiness["ready"]:
        print("\n[BLOCKED] Live publishing is disabled until credentials and approval are present.")
        print("Create the required config files and set LIVE_PUBLISH_APPROVED=true to proceed.")
        return

    summary = team.run_daily_cycle(max_videos=args.max_videos, live_mode=True, dry_run=False)
    print(json.dumps({
        "batch_size": summary["batch_size"],
        "live_mode": summary["live_mode"],
        "dry_run": summary["dry_run"],
        "overall_health": summary["agent_dashboard"]["overall_health"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
