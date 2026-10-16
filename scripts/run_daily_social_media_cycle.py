#!/usr/bin/env python3
"""Runs the social-media agent team for a single daily production cycle."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.social_media_team.agent_team import SocialMediaAgentTeam


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Run the daily social-media agent team")
    parser.add_argument("--config", type=str, default=str(base_dir / "config" / "config.json"), help="Path to the config JSON file")
    parser.add_argument("--max-videos", type=int, default=3, help="How many videos to plan in the cycle")
    parser.add_argument("--live", action="store_true", help="Attempt real upload if the source video exists and valid credentials are present")
    parser.add_argument("--no-dry-run", action="store_true", help="Disable safe dry-run mode even when no live video exists")
    args = parser.parse_args()

    team = SocialMediaAgentTeam(config_path=args.config)
    dry_run = not args.no_dry_run
    summary = team.run_daily_cycle(max_videos=args.max_videos, live_mode=args.live, dry_run=dry_run)
    out_path = BASE_DIR / "data" / "ops_command_center_status.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "generated_at": summary["generated_at"],
        "batch_size": summary["batch_size"],
        "live_mode": summary["live_mode"],
        "dry_run": summary["dry_run"],
        "job_flow": summary["job_flow"],
        "items": summary["items"],
        "quality_checks": summary["quality_checks"],
        "platform_mix": summary["platform_mix"],
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
