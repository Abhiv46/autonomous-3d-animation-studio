#!/usr/bin/env python3
"""Create an evidence-based YouTube/TikTok channel diagnosis report."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.channel_doctor.doctor_agent import (
    ChannelDoctorAgent,
    load_json,
    parse_tiktok_raw_page,
)
from agents.channel_doctor.action_executor import (
    ChannelDoctorActionExecutor,
    load_action_plan,
)
from browser.engine.pinned_brave import DEFAULT_CDP_ENDPOINT, ensure_pinned_brave


def capture_live_studio(config: dict) -> dict:
    from playwright.sync_api import sync_playwright

    ensure_pinned_brave()
    youtube_cfg = config.get("platforms", {}).get("youtube", {})
    channel_id = youtube_cfg.get("channel_id")
    if not channel_id:
        raise ValueError("YouTube channel_id is not configured; cannot inspect its Studio.")

    export = {
        "as_of": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "youtube": {"as_of": None, "channel": {}, "videos": []},
        "tiktok": {"as_of": None, "channel": {}, "videos": []},
    }
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(DEFAULT_CDP_ENDPOINT)
        context = browser.contexts[0]
        page = context.new_page()
        try:
            page.goto(
                "https://studio.youtube.com/",
                wait_until="domcontentloaded",
                timeout=45000,
            )
            page.locator("body").wait_for(timeout=20000)
            page.wait_for_timeout(4000)
            actual_channel_id = re.search(r"/channel/([^/?]+)", page.url)
            if not actual_channel_id or actual_channel_id.group(1) != channel_id:
                raise ValueError(
                    f"Configured YouTube channel ID {channel_id} does not match "
                    f"the channel currently selected in Studio ({actual_channel_id.group(1) if actual_channel_id else 'unknown'})."
                )
            dashboard_lines = [
                line.strip()
                for line in page.locator("body").inner_text().splitlines()
                if line.strip()
            ]
            current_subscribers_index = next(
                (
                    i for i, line in enumerate(dashboard_lines)
                    if line == "Current subscribers"
                ),
                None,
            )
            current_subscribers = None
            if (
                current_subscribers_index is not None
                and current_subscribers_index + 1 < len(dashboard_lines)
            ):
                current_subscribers = _parse_compact_number(
                    dashboard_lines[current_subscribers_index + 1]
                )
            analytics_link = page.get_by_role("link", name="Go to channel analytics")
            analytics_link.wait_for(state="visible", timeout=15000)
            analytics_link.click()
            page.get_by_text("Your top content in this period", exact=True).wait_for(
                state="visible",
                timeout=25000,
            )
            youtube_text = page.locator("body").inner_text()
            yt_lines = [line.strip() for line in youtube_text.splitlines() if line.strip()]
            if "Channel analytics" in youtube_text and "Your channel" in youtube_text:
                actual_channel_id = re.search(r"/channel/([^/?]+)", page.url)
                if not actual_channel_id or actual_channel_id.group(1) != channel_id:
                    raise ValueError(
                        "The configured YouTube channel ID did not resolve to the configured Studio channel."
                    )
                yt_channel: dict = {}
                period_index = next(
                    (i for i, line in enumerate(yt_lines) if line == "Last 28 days"),
                    None,
                )
                if period_index is not None:
                    for label, key in (
                        ("Views", "views_last_28_days"),
                        ("Watch time (hours)", "watch_hours_last_28_days"),
                        ("Subscribers", "subscribers_gained_net_last_28_days"),
                    ):
                        for line in yt_lines[period_index:period_index + 25]:
                            if line == label:
                                value = next(
                                    (item for item in yt_lines[yt_lines.index(line, period_index) + 1:][:3]
                                     if _parse_compact_number(item) is not None),
                                    None,
                                )
                                if value is not None:
                                    yt_channel[key] = _parse_compact_number(value)
                                    yt_channel[f"{key}_display"] = value
                                break
                if period_index is not None:
                    subscribers_index = next(
                        (
                            i for i, line in enumerate(yt_lines[period_index:], period_index)
                            if line == "Subscribers"
                        ),
                        None,
                    )
                    if subscribers_index is not None and subscribers_index + 1 < len(yt_lines):
                        value = _parse_compact_number(yt_lines[subscribers_index + 1])
                        if value is not None:
                            yt_channel["subscribers_gained_net_last_28_days"] = value
                            yt_channel["subscribers_gained_net_last_28_days_display"] = yt_lines[subscribers_index + 1]
                if current_subscribers is not None:
                    yt_channel["current_subscribers"] = current_subscribers
                export["youtube"] = {
                    "as_of": export["as_of"],
                    "channel": yt_channel,
                    "videos": _parse_youtube_top_content(yt_lines),
                    "latest_video": _latest_youtube_video(yt_lines),
                    "data_source": "authenticated YouTube Studio analytics overview",
                }
            else:
                export["youtube"]["unavailable_reason"] = (
                    "Pinned Brave did not show the configured YouTube Studio channel dashboard."
                )
        finally:
            page.close()

        page = context.new_page()
        try:
            page.goto(
                "https://www.tiktok.com/tiktokstudio/content",
                wait_until="domcontentloaded",
                timeout=45000,
            )
            page.locator("body").wait_for(timeout=20000)
            page.get_by_text(re.compile(r"\bPosts\s+\d+"), exact=False).wait_for(
                state="visible",
                timeout=25000,
            )
            page.wait_for_timeout(1000)
            tiktok_text = page.locator("body").inner_text()
            posts = parse_tiktok_raw_page(tiktok_text)
            posts_count_match = re.search(r"\bPosts\s+([\d,]+)", tiktok_text)
            if posts:
                export["tiktok"] = {
                    "as_of": export["as_of"],
                    "channel": {
                        "posts_count": int(posts_count_match.group(1).replace(",", ""))
                        if posts_count_match else None
                    },
                    "videos": posts,
                    "data_source": "authenticated TikTok Studio content page",
                }
            else:
                export["tiktok"]["unavailable_reason"] = (
                    "Pinned Brave did not expose parseable TikTok Studio post rows."
                )
        finally:
            page.close()
            playwright.stop()
    return export


def _parse_compact_number(value: str):
    match = re.fullmatch(r"\s*([+-]?[\d,.]+)\s*([kKmM]?)\s*", value)
    if not match:
        return None
    number = float(match.group(1).replace(",", ""))
    multiplier = {"k": 1000, "m": 1000000}.get(match.group(2).casefold(), 1)
    scaled = number * multiplier
    return int(scaled) if scaled.is_integer() else scaled


def _parse_youtube_top_content(lines: list[str]) -> list[dict]:
    try:
        start = lines.index("Your top content in this period") + 1
        end = lines.index("See more", start)
    except ValueError:
        return []
    section = lines[start:end]
    rank_indexes = [
        i for i, line in enumerate(section)
        if re.fullmatch(r"\d+", line)
        and 1 <= int(line) <= 10
        and i + 2 < len(section)
        and re.search(r"\b[A-Za-z]{3,9}\s+\d{1,2},\s+\d{4}\b", section[i + 2])
    ]
    videos = []
    for position, rank_index in enumerate(rank_indexes):
        row_end = rank_indexes[position + 1] if position + 1 < len(rank_indexes) else len(section)
        row = section[rank_index + 1:row_end]
        if len(row) < 4:
            continue
        title = row[0]
        duration_index = next((i for i, line in enumerate(row) if re.fullmatch(r"\d+:\d{2}", line)), None)
        if duration_index is None or duration_index + 2 >= len(row):
            continue
        duration_parts = [int(part) for part in row[duration_index].split(":")]
        duration_seconds = duration_parts[0] * 60 + duration_parts[1]
        percent_match = re.fullmatch(r"\(([\d.]+)%\)", row[duration_index + 1])
        views = _parse_compact_number(row[duration_index + 2])
        video = {"title": title, "duration_seconds": duration_seconds}
        if percent_match:
            video["average_percentage_viewed"] = float(percent_match.group(1))
            video["average_watch_time_seconds"] = round(
                duration_seconds * float(percent_match.group(1)) / 100,
                2,
            )
        if views is not None:
            video["views"] = views
        videos.append(video)
    return videos


def _latest_youtube_video(lines: list[str]) -> dict:
    try:
        start = lines.index("Latest content") + 1
        end = lines.index("See video analytics", start)
    except ValueError:
        return {}
    section = lines[start:end]
    if len(section) < 3:
        return {}
    latest = {"title": section[0]}
    age = next((line for line in section if re.fullmatch(r"First \d+ .+", line)), None)
    if age:
        latest["observed_age"] = age
    views_index = next((i for i, line in enumerate(section) if line == "Views"), None)
    if views_index is not None and views_index + 1 < len(section):
        views = _parse_compact_number(section[views_index + 1])
        if views is not None:
            latest["views"] = views
    percent_index = next((i for i, line in enumerate(section) if line == "Average percentage viewed"), None)
    if percent_index is not None and percent_index + 1 < len(section):
        latest["average_percentage_viewed"] = _parse_compact_number(section[percent_index + 1])
    return latest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Diagnose channels and optionally execute an explicit, validated action plan."
    )
    parser.add_argument(
        "--studio-export",
        type=Path,
        help="Optional JSON export with youtube.videos and tiktok.videos metrics.",
    )
    parser.add_argument(
        "--live-studio",
        action="store_true",
        help="Read visible YouTube/TikTok Studio dashboards using the pinned Brave session.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE_DIR / "data" / "channel_doctor_report.json",
    )
    parser.add_argument(
        "--actions",
        type=Path,
        help="JSON action plan. Without --execute-actions, actions are validated and dry-run only.",
    )
    parser.add_argument(
        "--execute-actions",
        action="store_true",
        help="Apply the supplied action plan live. Requires --live-studio and saved approval.",
    )
    args = parser.parse_args()
    if args.execute_actions and not args.actions:
        parser.error("--execute-actions requires --actions.")
    if args.execute_actions and not args.live_studio:
        parser.error("--execute-actions requires --live-studio to refresh live evidence.")

    config = load_json(BASE_DIR / "config" / "config.json")
    harvest = load_json(BASE_DIR / "data" / "tiktok_studio_analytics_harvest.json")
    upload_log_path = BASE_DIR.parent / "uploaded_videos_log.json"
    upload_log = load_json(upload_log_path)
    if args.live_studio:
        studio_export = capture_live_studio(config)
        export_path = BASE_DIR / "data" / "channel_doctor_live_export.json"
        export_path.parent.mkdir(parents=True, exist_ok=True)
        export_temporary = export_path.with_suffix(".json.tmp")
        export_temporary.write_text(
            json.dumps(studio_export, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        export_temporary.replace(export_path)
    else:
        studio_export = load_json(args.studio_export)
    platform_cfg = config.get("platforms", {})

    doctor = ChannelDoctorAgent(
        youtube_handle=platform_cfg.get("youtube", {}).get("channel_handle", ""),
        tiktok_handle=platform_cfg.get("tiktok", {}).get("channel_handle"),
    )
    report = doctor.diagnose(
        tiktok_harvest=harvest,
        upload_log=upload_log,
        studio_export=studio_export,
    )
    if args.actions:
        action_plan = load_action_plan(args.actions)
        executor = ChannelDoctorActionExecutor(config=config, repo_root=BASE_DIR)
        report["action_execution"] = executor.execute(
            action_plan,
            dry_run=not args.execute_actions,
        )
        report["scope"]["publishing_or_deleting_performed"] = report[
            "action_execution"
        ]["live_actions_performed"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(args.output)

    print(f"Assessment: {report['overall_assessment']}")
    print(f"Findings: {len(report['findings'])}; report: {args.output}")
    for item in report["findings"]:
        print(f"- [{item['severity'].upper()}][{item['evidence_type']}] {item['summary']}")
    if "action_execution" in report:
        execution = report["action_execution"]
        print(
            f"Action mode: {execution['mode']}; "
            f"live changes performed: {execution['live_actions_performed']}"
        )
        for result in execution["results"]:
            print(
                f"- [{result.get('status', 'UNKNOWN')}] "
                f"{result.get('platform')} {result.get('operation')} "
                f"{result.get('video_id')}: "
                f"{result.get('reason', result.get('message', ''))}"
            )
    else:
        print("No channel settings, videos, uploads, or account data were changed.")


if __name__ == "__main__":
    main()
