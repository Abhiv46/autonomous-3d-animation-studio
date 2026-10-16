#!/usr/bin/env python3
"""Runs the social-media agent team and persists a safe daily production plan."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.social_media_team.agent_team import SocialMediaAgentTeam


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the daily social-media batch cycle")
    parser.add_argument("--config", type=str, default=str(BASE_DIR / "config" / "config.json"), help="Path to the config JSON")
    parser.add_argument("--max-videos", type=int, default=3, help="How many video tasks to generate")
    parser.add_argument("--live", action="store_true", help="Allow live upload attempt if source files and credentials are available")
    parser.add_argument("--no-dry-run", action="store_true", help="Disable safe dry-run guard")
    args = parser.parse_args()

    team = SocialMediaAgentTeam(config_path=args.config)
    summary = team.run_daily_cycle(
        max_videos=args.max_videos,
        live_mode=args.live,
        dry_run=not args.no_dry_run,
    )

    out_path = BASE_DIR / "data" / "daily_social_media_plan.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    queue_path = BASE_DIR / "data" / "ops_command_center_status.json"
    queue_path.write_text(json.dumps({
        "generated_at": summary["generated_at"],
        "batch_size": summary["batch_size"],
        "live_mode": summary["live_mode"],
        "dry_run": summary["dry_run"],
        "job_flow": summary["job_flow"],
        "items": summary["items"],
        "quality_checks": summary["quality_checks"],
        "platform_mix": summary["platform_mix"],
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "output_file": str(out_path),
        "queue_file": str(queue_path),
        "batch_size": summary["batch_size"],
        "platform_mix": summary["platform_mix"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
