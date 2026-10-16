#!/usr/bin/env python3
"""Safe live dispatch for the social-media agent team.

This script takes a prepared daily batch and only attempts live uploads when the
source video file exists and the caller explicitly requests live publishing.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.social_media_team.agent_team import SocialMediaAgentTeam


def main() -> None:
    parser = argparse.ArgumentParser(description="Safely dispatch a prepared social-media batch")
    parser.add_argument("--config", type=str, default=str(BASE_DIR / "config" / "config.json"), help="Path to the config JSON")
    parser.add_argument("--max-videos", type=int, default=3, help="Number of prepared tasks to dispatch")
    parser.add_argument("--live", action="store_true", help="Attempt actual uploads when source video files are present")
    parser.add_argument("--no-dry-run", action="store_true", help="Disable the default dry-run guard")
    args = parser.parse_args()

    team = SocialMediaAgentTeam(config_path=args.config)
    batch = team.plan_daily_batch(max_videos=args.max_videos)

    for item in batch:
        platform = item["platform"]
        candidate_path = BASE_DIR / "data" / "output" / f"{item['id']}_{platform}.mp4"
        if candidate_path.exists():
            item["publishing_payload"]["video_path"] = str(candidate_path)
        elif not args.live:
            item["publishing_payload"]["video_path"] = "" 

    if not args.live:
        print(json.dumps({
            "mode": "dry_run",
            "prepared_batch": [{
                "id": item["id"],
                "title": item["title"],
                "platform": item["platform"],
                "account_email": item["account"].get("email"),
                "video_ready": os.path.exists(item["publishing_payload"].get("video_path", "")),
            } for item in batch],
        }, ensure_ascii=False, indent=2))
        return

    dry_run = not args.no_dry_run
    summary = team.run_daily_cycle(max_videos=args.max_videos, live_mode=True, dry_run=dry_run)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
