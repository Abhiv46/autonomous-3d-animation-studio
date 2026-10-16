#!/usr/bin/env python3
"""Obtain YouTube upload/edit authorization in the pinned Brave profile."""

from __future__ import annotations

import argparse
import json
import pickle
import sys
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from browser.engine.pinned_brave import DEFAULT_CDP_ENDPOINT, ensure_pinned_brave
from platforms.live_production import LiveProductionGate

YOUTUBE_SCOPES = (
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
)


def verify_authorized_channel(
    service,
    expected_channel_id: str,
) -> dict:
    response = service.channels().list(part="id,snippet", mine=True).execute()
    channels = response.get("items", [])
    if len(channels) != 1:
        raise PermissionError(
            f"Google returned {len(channels)} YouTube channels; expected exactly one."
        )
    channel = channels[0]
    actual_channel_id = channel.get("id")
    if actual_channel_id != expected_channel_id:
        raise PermissionError(
            "The authorized Google account does not own the configured YouTube channel; "
            "the OAuth token was not saved."
        )
    return {
        "channel_id": actual_channel_id,
        "channel_title": channel.get("snippet", {}).get("title"),
    }


def _open_in_pinned_brave(
    url: str,
    new: int = 0,
    autoraise: bool = True,
) -> bool:
    from playwright.sync_api import sync_playwright

    ensure_pinned_brave()
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(
            DEFAULT_CDP_ENDPOINT,
            timeout=10000,
        )
        if not browser.contexts:
            raise RuntimeError("Pinned Brave has no available browser context.")
        page = browser.contexts[0].new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        return True


def _oauth_client_path(config: dict, explicit_path: Path | None) -> Path:
    gate = LiveProductionGate(config=config, repo_root=str(BASE_DIR))
    if explicit_path:
        path = explicit_path.expanduser().resolve()
    else:
        path = Path(gate._default_paths()["youtube_client_secret"])
    if not path.is_file():
        raise FileNotFoundError(f"Google OAuth client file not found: {path}")

    client_data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(client_data.get("installed"), dict):
        raise ValueError("Expected a Google installed-app OAuth client JSON file.")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Authorize YouTube uploads and metadata management in pinned Brave."
    )
    parser.add_argument(
        "--client-secrets",
        type=Path,
        help="OAuth client JSON path; defaults to the discovered adjacent file.",
    )
    parser.add_argument(
        "--token-output",
        type=Path,
        default=BASE_DIR / "config" / "token.pickle",
        help="Local path for the OAuth token.",
    )
    args = parser.parse_args()

    config = json.loads(
        (BASE_DIR / "config" / "config.json").read_text(encoding="utf-8-sig")
    )
    youtube_config = config.get("platforms", {}).get("youtube", {})
    expected_channel_id = youtube_config.get("channel_id")
    if not expected_channel_id:
        raise ValueError("No target YouTube channel ID is configured.")

    token_path = args.token_output.resolve()
    if token_path.exists():
        raise FileExistsError(
            f"Refusing to overwrite an existing YouTube token: {token_path}"
        )

    client_path = _oauth_client_path(config, args.client_secrets)
    ensure_pinned_brave()

    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    flow = InstalledAppFlow.from_client_secrets_file(
        str(client_path),
        scopes=list(YOUTUBE_SCOPES),
    )
    original_open = webbrowser.open
    webbrowser.open = _open_in_pinned_brave
    try:
        credentials = flow.run_local_server(
            host="127.0.0.1",
            port=0,
            open_browser=True,
            authorization_prompt_message="Approve YouTube access in the pinned Brave window.",
            success_message="YouTube authorization received. You can close this tab.",
            access_type="offline",
            prompt="consent",
        )
    finally:
        webbrowser.open = original_open

    if not credentials.has_scopes(YOUTUBE_SCOPES):
        raise PermissionError(
            "Google did not grant both requested YouTube scopes; token was not saved."
        )

    service = build("youtube", "v3", credentials=credentials)
    verified_channel = verify_authorized_channel(service, expected_channel_id)

    token_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = token_path.with_suffix(token_path.suffix + ".tmp")
    try:
        with temporary_path.open("xb") as token_file:
            pickle.dump(credentials, token_file)
        temporary_path.replace(token_path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()

    print(
        json.dumps(
            {
                "authorized": True,
                "channel_id": verified_channel["channel_id"],
                "channel_title": verified_channel["channel_title"],
                "granted_scopes": list(credentials.scopes or []),
                "token_saved_to": str(token_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
