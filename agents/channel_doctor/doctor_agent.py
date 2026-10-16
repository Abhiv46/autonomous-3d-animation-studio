from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional


class ChannelDoctorAgent:
    """Audits available channel evidence and proposes evidence-labeled fixes."""

    def __init__(
        self,
        youtube_handle: str,
        tiktok_handle: Optional[str] = None,
        stale_after_days: int = 3,
    ):
        self.youtube_handle = youtube_handle
        self.tiktok_handle = tiktok_handle
        self.stale_after_days = stale_after_days

    def diagnose(
        self,
        tiktok_harvest: Optional[dict] = None,
        upload_log: Optional[dict] = None,
        studio_export: Optional[dict] = None,
        now: Optional[datetime] = None,
    ) -> dict:
        observed_at = now or datetime.now(timezone.utc)
        studio_export = studio_export or {}
        youtube_data = studio_export.get("youtube", {})
        tiktok_data = studio_export.get("tiktok", {})
        findings: list[dict[str, Any]] = []
        repairs: list[dict[str, str]] = []

        yt_videos = _valid_videos(youtube_data.get("videos", []))
        tt_videos = _valid_videos(tiktok_data.get("videos", []))
        if yt_videos:
            findings.extend(self._diagnose_metrics("youtube", yt_videos, youtube_data, observed_at))
        else:
            findings.append(
                _finding(
                    "YOUTUBE_ANALYTICS_MISSING",
                    "high",
                    "hypothesis",
                    "No usable YouTube Studio video metrics were supplied. Public channel data and upload logs cannot reveal Shorts retention, viewed-vs-swiped, or traffic sources.",
                    ["Export YouTube Studio analytics for the last 28 days, including video-level views, average view duration, average percentage viewed, shown in feed, and viewed-vs-swiped."],
                )
            )
        youtube_channel = youtube_data.get("channel", {})
        if youtube_channel:
            channel_metrics = {
                key: value
                for key, value in youtube_channel.items()
                if key in {
                    "subscribers",
                    "current_subscribers",
                    "views_last_28_days",
                    "watch_hours_last_28_days",
                    "subscribers_gained_net_last_28_days",
                }
                and value is not None
            }
            if channel_metrics:
                findings.append(
                    _finding(
                        "YOUTUBE_CHANNEL_STUDIO_SNAPSHOT",
                        "low",
                        "verified",
                        "YouTube Studio currently reports " + ", ".join(
                            f"{key.replace('_', ' ')}: {value}" for key, value in channel_metrics.items()
                        ) + ". These are channel-level totals, not proof of which video factor caused reach.",
                        ["Use per-Short feed exposure and retention data to diagnose individual videos."],
                    )
                )
            channel_views = _number(youtube_channel.get("views_last_28_days"))
            top_three_views = sorted(
                (float(value) for value in (
                    _number(video.get("views")) for video in yt_videos
                ) if value is not None),
                reverse=True,
            )[:3]
            if channel_views and len(top_three_views) == 3:
                top_three_share = sum(top_three_views) / channel_views * 100
                findings.append(
                    _finding(
                        "YOUTUBE_TOP_CONTENT_CONCENTRATION",
                        "low",
                        "verified",
                        f"The three highest-viewed supplied videos account for about {top_three_share:.0f}% of YouTube Studio's 28-day channel views. Studio's displayed channel total is rounded, so this share is approximate.",
                        ["Study what differs in the top videos, then test one original hook/pacing variation at a time rather than repeating titles or scenes."],
                    )
                )

        harvest_posts: list[dict[str, Any]] = []
        harvest_at = None
        if tiktok_harvest and (
            studio_export is None or "tiktok" not in studio_export
        ):
            harvest_at = _parse_date(tiktok_harvest.get("harvested_at"))
            harvest_posts = _valid_videos(tiktok_harvest.get("post_rows", []))
            if not harvest_posts:
                harvest_posts = parse_tiktok_raw_page(str(tiktok_harvest.get("raw_page_text", "")))
        if tt_videos:
            findings.extend(self._diagnose_metrics("tiktok", tt_videos, tiktok_data, observed_at))
        elif harvest_posts:
            findings.extend(
                self._diagnose_metrics(
                    "tiktok",
                    harvest_posts,
                    {"as_of": tiktok_harvest.get("harvested_at")},
                    observed_at,
                )
            )
        tiktok_channel = tiktok_data.get("channel", {})
        if tiktok_channel.get("posts_count") is not None:
            findings.append(
                _finding(
                    "TIKTOK_STUDIO_POST_COUNT",
                    "low",
                    "verified",
                    f"TikTok Studio displays {tiktok_channel['posts_count']} posts. This confirms account activity, not current reach or monetization eligibility.",
                    ["Review the latest post-level watch time, completion, shares, and traffic-source metrics."],
                )
            )
        burst = _posting_burst(tt_videos, observed_at)
        if burst:
            count, window_minutes = burst
            findings.append(
                _finding(
                    "TIKTOK_POSTING_BURST",
                    "medium",
                    "verified",
                    f"The current Studio snapshot shows {count} posts within about {window_minutes} minutes. That pacing is observable; any effect on distribution is unproven.",
                    ["Test a more spaced schedule on the next comparable batch and compare equal-age metrics; do not delete or repost these videos."],
                )
            )
            if harvest_at and observed_at - _aware(harvest_at) > timedelta(days=self.stale_after_days):
                findings.append(
                    _finding(
                        "TIKTOK_SNAPSHOT_STALE",
                        "medium",
                        "verified",
                        f"The available TikTok Studio snapshot is older than {self.stale_after_days} days; do not treat its counts as current.",
                        ["Capture/export the last 28 days from TikTok Studio before changing a live content strategy."],
                    )
                )
        else:
            findings.append(
                _finding(
                    "TIKTOK_ANALYTICS_MISSING",
                    "high",
                    "hypothesis",
                    "No structured current TikTok Studio post metrics were supplied. The local harvest has no parseable post rows.",
                    ["Export TikTok Studio post analytics for the last 28 days, including views, average watch time, full-video watch rate, likes, comments, shares, and traffic sources."],
                )
            )

        if upload_log:
            findings.extend(self._diagnose_upload_log(upload_log))
        else:
            findings.append(
                _finding(
                    "UPLOAD_HISTORY_MISSING",
                    "medium",
                    "hypothesis",
                    "No upload-history file was available to verify posting cadence or duplicate publication.",
                    ["Keep a platform-ID-backed upload log and verify suspected duplicate titles in each official Studio."],
                )
            )

        if not self.tiktok_handle:
            findings.append(
                _finding(
                    "TIKTOK_HANDLE_UNCONFIGURED",
                    "low",
                    "verified",
                    "The repository does not configure the actual TikTok handle, so account identity cannot be independently cross-checked.",
                    ["Set the real TikTok handle in config after confirming it in TikTok Studio."],
                )
            )

        repairs.extend(
            [
                {
                    "id": "tiktok_structured_row_extraction",
                    "status": "fixed_in_code",
                    "detail": "The Studio scraper now falls back to role-based rows when table rows are absent and extracts visible data rows from the pinned Brave session.",
                },
                {
                    "id": "synthetic_zero_analytics",
                    "status": "fixed_in_code",
                    "detail": "Platform adapters now report analytics as unavailable instead of inventing zero views and likes.",
                },
                {
                    "id": "youtube_channel_target",
                    "status": "corrected_after_studio_verification",
                    "detail": "The configured YouTube channel ID was corrected to the ID linked from the signed-in The Naughty Duo Studio dashboard.",
                },
                {
                    "id": "preset_growth_scores",
                    "status": "fixed_in_code",
                    "detail": "The doctor labels missing evidence explicitly and does not present static targets as measured performance.",
                },
            ]
        )

        return {
            "generated_at": observed_at.isoformat(timespec="seconds"),
            "scope": {
                "youtube_handle": self.youtube_handle,
                "tiktok_handle": self.tiktok_handle,
                "promises_of_virality": False,
                "publishing_or_deleting_performed": False,
            },
            "overall_assessment": (
                "INSUFFICIENT_CURRENT_ANALYTICS"
                if not yt_videos or not (tt_videos or (harvest_posts and harvest_at and observed_at - _aware(harvest_at) <= timedelta(days=self.stale_after_days)))
                else "EVIDENCE_BASED_REVIEW"
            ),
            "data_coverage": {
                "youtube_posts_analyzed": len(yt_videos),
                "youtube_as_of": youtube_data.get("as_of"),
                "youtube_source": youtube_data.get("data_source", "manual export" if yt_videos else "unavailable"),
                "tiktok_posts_analyzed": len(tt_videos or harvest_posts),
                "tiktok_as_of": tiktok_data.get("as_of") or (tiktok_harvest or {}).get("harvested_at"),
                "tiktok_source": tiktok_data.get(
                    "data_source",
                    "legacy local harvest" if harvest_posts else "unavailable",
                ),
                "limitations": [
                    "Studio UI snapshot includes visible rows, not necessarily every post.",
                    "Retention graphs, swipe decisions, traffic sources, and share counts require their dedicated Studio analytics views.",
                ],
            },
            "findings": findings,
            "safe_fixes_applied": repairs,
            "next_experiment": {
                "rule": "Change one variable at a time and compare against the channel's own recent baseline.",
                "youtube": "Test first-second hook clarity while holding topic, duration, and posting window as constant as practical.",
                "tiktok": "Test searchable on-screen/caption phrasing and a visible payoff; compare average watch time, full-video watch rate, and shares.",
                "approval_boundary": "Live metadata edits and evidence-qualified deletions require an explicit action plan and --execute-actions. Paid promotion is not supported.",
            },
        }

    def _diagnose_metrics(
        self,
        platform: str,
        videos: list[dict[str, Any]],
        container: dict,
        observed_at: datetime,
    ) -> list[dict[str, Any]]:
        findings = []
        date_value = container.get("as_of") or container.get("harvested_at")
        captured_at = _parse_date(date_value)
        if captured_at and observed_at - _aware(captured_at) > timedelta(days=self.stale_after_days):
            findings.append(
                _finding(
                    f"{platform.upper()}_ANALYTICS_STALE",
                    "medium",
                    "verified",
                    f"The supplied {platform} metrics are older than {self.stale_after_days} days.",
                    ["Refresh the same analytics date range before making changes based on these counts."],
                )
            )

        view_values = [float(row["views"]) for row in videos if _number(row.get("views")) is not None]
        if view_values:
            median_views = _median(view_values)
            findings.append(
                _finding(
                    f"{platform.upper()}_OWN_BASELINE",
                    "low",
                    "verified",
                    f"{len(view_values)} supplied posts have view counts; their median is {median_views:g}. This is an internal comparison only, not an algorithm benchmark.",
                    ["Compare each post to this account's own baseline using the same post-age window."],
                )
            )

        if platform == "youtube":
            retention_rows = [
                row for row in videos
                if _number(row.get("average_percentage_viewed")) is not None
            ]
            if len(retention_rows) >= 3:
                comparable_rows = sorted(
                    retention_rows,
                    key=lambda row: _number(row.get("views")) or 0,
                    reverse=True,
                )[:3]
                best = max(comparable_rows, key=lambda row: float(row["average_percentage_viewed"]))
                weakest = min(comparable_rows, key=lambda row: float(row["average_percentage_viewed"]))
                findings.append(
                    _finding(
                        "YOUTUBE_RETENTION_SPREAD",
                        "medium",
                        "verified",
                        f"Among the {len(comparable_rows)} highest-viewed supplied videos, average percentage viewed ranges from {float(weakest['average_percentage_viewed']):g}% to {float(best['average_percentage_viewed']):g}%. This identifies a test opportunity, not a proven causal format difference.",
                        [
                            f"Use the higher-retention video ({best.get('title', 'top video')}) as one reference; test its hook/pacing against a new original idea.",
                            f"Review the early drop-off on the lower-retention video ({weakest.get('title', 'lowest video')}) in per-video retention graphs."
                        ],
                    )
                )
            if not any(_number(v.get("average_percentage_viewed")) is not None or _number(v.get("average_view_duration_seconds")) is not None for v in videos):
                findings.append(
                    _finding(
                        "YOUTUBE_RETENTION_MISSING",
                        "high",
                        "hypothesis",
                        "No supplied YouTube video has average view duration or average percentage viewed; opening-hook and pacing causes cannot be isolated.",
                        ["Add average view duration and average percentage viewed for each Short."],
                    )
                )
            if not any(_number(v.get("viewed_vs_swiped_away")) is not None or _number(v.get("shown_in_feed")) is not None for v in videos):
                findings.append(
                    _finding(
                        "YOUTUBE_SHORTS_FEED_MISSING",
                        "high",
                        "hypothesis",
                        "Shorts feed exposure and viewed-vs-swiped data are missing, so distribution versus creative performance cannot be separated.",
                        ["Add shown-in-feed and viewed-vs-swiped metrics from YouTube Studio."],
                    )
                )
            latest_video = container.get("latest_video")
            if latest_video and latest_video.get("observed_age"):
                findings.append(
                    _finding(
                        "YOUTUBE_LATEST_VIDEO_TOO_EARLY_TO_JUDGE",
                        "low",
                        "verified",
                        f"The latest Studio card is only {latest_video['observed_age']} old; its early view count is not a reliable performance diagnosis yet.",
                        ["Recheck after at least 24-48 hours and compare with videos at the same age."],
                    )
                )
        else:
            required = ("average_watch_time_seconds", "full_video_watch_rate", "shares")
            missing = [name for name in required if not any(_number(v.get(name)) is not None for v in videos)]
            if missing:
                findings.append(
                    _finding(
                        "TIKTOK_RETENTION_AND_SHARES_MISSING",
                        "high",
                        "hypothesis",
                        "The supplied TikTok posts do not include all diagnostic fields: " + ", ".join(missing) + ".",
                        ["Add average watch time, full-video watch rate, and shares before attributing low reach to a particular cause."],
                    )
                )
            durations = [float(v["duration_seconds"]) for v in videos if _number(v.get("duration_seconds")) is not None]
            if durations and max(durations) < 60:
                findings.append(
                    _finding(
                        "TIKTOK_POSTS_UNDER_60_SECONDS",
                        "medium",
                        "verified",
                        f"All {len(durations)} parseable supplied TikTok posts are under 60 seconds. This may limit eligibility for some longer-video monetization programs, but is not proof of reduced reach.",
                        ["Check current regional program eligibility; test a story that earns a longer duration rather than adding filler."],
                    )
                )

        generic_tags = 0
        repeated_tag_posts = 0
        for row in videos:
            caption = str(row.get("caption") or row.get("title") or "")
            tags = re.findall(r"#[\w]+", caption.casefold())
            generic_tags += sum(tag in {"#viral", "#fyp", "#foryou", "#trending", "#fy"} for tag in tags)
            if len(tags) >= 8:
                repeated_tag_posts += 1
        if generic_tags or repeated_tag_posts:
            hashtag_word = "hashtag" if generic_tags == 1 else "hashtags"
            caption_word = "caption" if repeated_tag_posts == 1 else "captions"
            findings.append(
                _finding(
                    f"{platform.upper()}_GENERIC_HASHTAG_OVERUSE",
                    "low",
                    "verified",
                    f"Among supplied captions, {generic_tags} generic reach {hashtag_word} and {repeated_tag_posts} {caption_word} with 8+ hashtags were found. This is a metadata quality issue, not proof of suppression.",
                    ["Replace broad tag piles with a few accurate topic, language, and audience phrases; do not promise that hashtags alone increase reach."],
                )
            )
        return findings

    def _diagnose_upload_log(self, upload_log: dict) -> list[dict[str, Any]]:
        records = upload_log.get("uploaded", [])
        if not isinstance(records, list):
            return [
                _finding(
                    "UPLOAD_LOG_INVALID",
                    "medium",
                    "verified",
                    "The upload log does not contain an uploaded-record list.",
                    ["Provide a valid upload log before diagnosing cadence or duplicates."],
                )
            ]
        findings = []
        for field, platform in (("youtube_title", "YOUTUBE"), ("tiktok_caption", "TIKTOK")):
            titles = [
                _normalize_title(str(row.get(field, "")))
                for row in records
                if isinstance(row, dict) and row.get(field)
            ]
            repeats = [(title, count) for title, count in Counter(titles).items() if count > 1]
            if repeats:
                findings.append(
                    _finding(
                        f"{platform}_POSSIBLE_DUPLICATE_UPLOADS",
                        "medium",
                        "verified",
                        f"The local log contains {len(repeats)} repeated {platform} title group(s); this does not prove multiple public posts because the log can include drafts, retries, or privacy changes.",
                        ["Cross-check platform video IDs and visibility in official Studio before deleting, privating, or re-uploading anything."],
                    )
                )
        stamped = [
            _parse_date(row.get("timestamp"))
            for row in records
            if isinstance(row, dict) and row.get("timestamp")
        ]
        stamped = [_aware(value) for value in stamped if value]
        if stamped:
            latest = max(stamped)
            if _aware(datetime.now(timezone.utc)) - latest > timedelta(days=self.stale_after_days):
                findings.append(
                    _finding(
                        "UPLOAD_LOG_STALE",
                        "medium",
                        "verified",
                        f"The newest timestamp in the local upload log is {latest.date().isoformat()}; it is older than {self.stale_after_days} days.",
                        ["Verify recent live uploads in each platform's Studio; local logs are not authoritative publication records."],
                    )
                )
        return findings


def parse_tiktok_raw_page(text: str) -> list[dict[str, Any]]:
    """Parses visible legacy TikTok Studio rows when structured extraction is empty."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    duration_pattern = re.compile(r"^\d{1,2}:\d{2}$")
    number_pattern = re.compile(r"^\d[\d,]*$")
    rows: list[dict[str, Any]] = []
    starts = [index for index, line in enumerate(lines) if duration_pattern.fullmatch(line)]
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        block = lines[start:end]
        public_index = next((i for i, value in enumerate(block) if value.casefold() in {"public", "friends", "private"}), None)
        if public_index is None:
            continue
        metric_lines = []
        for value in block[public_index + 1:]:
            if number_pattern.fullmatch(value):
                metric_lines.append(int(value.replace(",", "")))
            elif metric_lines:
                break
        if len(metric_lines) < 3:
            continue
        date_value = next((value for value in block if re.search(r"\b\d{1,2}\s+[A-Za-z]{3,9},", value)), None)
        title = next(
            (
                value for value in block[1:public_index]
                if not value.casefold().startswith("pinned")
                and not re.search(r"\b\d{1,2}\s+[A-Za-z]{3,9},", value)
            ),
            "",
        )
        minutes, seconds = (int(part) for part in block[0].split(":"))
        rows.append(
            {
                "title": title,
                "caption": title,
                "duration_seconds": minutes * 60 + seconds,
                "published_at": date_value,
                "views": metric_lines[0],
                "likes": metric_lines[1],
                "comments": metric_lines[2],
                "visibility": block[public_index],
            }
        )
    return rows


def load_json(path: Optional[Path]) -> Optional[dict]:
    if path is None or not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}.")
    return value


def _valid_videos(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _number(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(str(value).replace("%", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def _parse_date(value: Any) -> Optional[datetime]:
    if not value or not isinstance(value, str):
        return None
    normalized = value.strip().replace("Z", "+00:00")
    for candidate in (normalized, normalized.replace(" ", "T", 1)):
        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            continue
    return None


def _posting_burst(videos: list[dict[str, Any]], observed_at: datetime) -> Optional[tuple[int, int]]:
    parsed = []
    year = observed_at.year
    for row in videos:
        value = str(row.get("published_at") or "")
        normalized = value.replace("\u202f", " ").replace("\u00a0", " ").strip()
        for format_string in ("%d %b, %I:%M %p", "%d %B, %I:%M %p"):
            try:
                parsed.append(datetime.strptime(f"{normalized} {year}", f"{format_string} %Y"))
                break
            except ValueError:
                continue
    parsed.sort()
    best = None
    for start, first in enumerate(parsed):
        for end in range(start + 2, len(parsed)):
            minutes = int((parsed[end] - first).total_seconds() // 60)
            if minutes <= 60:
                candidate = (end - start + 1, minutes)
                if best is None or candidate[0] > best[0]:
                    best = candidate
            else:
                break
    return best


def _aware(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def _median(values: list[float]) -> float:
    sorted_values = sorted(values)
    middle = len(sorted_values) // 2
    if len(sorted_values) % 2:
        return sorted_values[middle]
    return (sorted_values[middle - 1] + sorted_values[middle]) / 2


def _normalize_title(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def _finding(
    finding_id: str,
    severity: str,
    evidence_type: str,
    summary: str,
    recommended_action: list[str],
) -> dict[str, Any]:
    return {
        "id": finding_id,
        "severity": severity,
        "evidence_type": evidence_type,
        "summary": summary,
        "recommended_action": recommended_action,
    }
