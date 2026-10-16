#!/usr/bin/env python3
"""Open one isolated Brave profile for Google Flow automation authentication."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.social_media_team.agent_team import SocialMediaAgentTeam


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Open a dedicated automation-only browser profile for one Google Flow account."
    )
    parser.add_argument("--slot", type=int, required=True, help="Configured Google Flow account slot (0-7)")
    args = parser.parse_args()

    team = SocialMediaAgentTeam()
    account = next(
        (
            item
            for item in team.accounts
            if int(item.get("slot_index", -1)) == args.slot
            and item.get("status") == "ACTIVE"
        ),
        None,
    )
    if account is None:
        raise SystemExit(f"No active Google Flow account is configured for slot {args.slot}.")

    browser_exe = os.getenv(
        "BRAVE_EXECUTABLE",
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    )
    if not Path(browser_exe).is_file():
        raise SystemExit(
            f"Brave executable not found at {browser_exe}. Set BRAVE_EXECUTABLE to the installed Brave path."
        )

    profile_dir = BASE_DIR / "browser_sessions" / f"flow_slot_{args.slot}"
    profile_dir.mkdir(parents=True, exist_ok=True)
    flow_url = "https://flow.google.com/"
    subprocess.Popen(
        [
            browser_exe,
            f"--user-data-dir={profile_dir}",
            "--no-first-run",
            flow_url,
        ],
        cwd=str(BASE_DIR),
    )
    print(f"Opened isolated Flow profile for slot {args.slot}: {account.get('email', 'configured account')}")
    print(f"Profile directory: {profile_dir}")
    print("Sign in to the intended Google account in this window, then close it before automation uses this slot.")


if __name__ == "__main__":
    main()
