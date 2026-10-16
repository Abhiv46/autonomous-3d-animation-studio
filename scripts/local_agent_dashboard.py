#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.social_media_team.agent_team import SocialMediaAgentTeam


def main() -> None:
    team = SocialMediaAgentTeam()
    batch = team.plan_daily_batch(max_videos=3)
    quality_results = team.quality_agent.evaluate_batch(batch)
    upload_results = team.publish_batch(
        batch,
        live_mode=False,
        dry_run=True,
        quality_results=quality_results,
    )
    dashboard = team.dashboard_agent.build_dashboard(batch, quality_results, upload_results)
    print(json.dumps({"agent_dashboard": dashboard}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
