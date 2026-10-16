import threading
from datetime import datetime

import pytest

from agents.worker_pool.parallel_engine import MultiAccountParallelEngine
from backend.db.database import DatabaseManager
from agents.channel_doctor.doctor_agent import ChannelDoctorAgent, parse_tiktok_raw_page
from browser.google_flow.credit_monitor import parse_credit_snapshot


class _NoDuplicate:
    def verify_zero_duplicate(self, title, prompts):
        return {"is_duplicate": False}


def test_parses_live_credits_and_daily_refresh_time():
    local_timezone = datetime.now().astimezone().tzinfo
    now = datetime(2026, 10, 7, 13, 59, tzinfo=local_timezone)
    snapshot = parse_credit_snapshot(
        "Lilly Looks\ninfolillylooks@gmail.com\n"
        "0 Google Flow credits\nCredits refresh daily at 7:41 PM",
        "infolillylooks@gmail.com",
        now=now,
    )

    assert snapshot.credits == 0
    assert snapshot.refresh_label == "7:41 PM"
    expected_refresh = now.replace(hour=19, minute=41).isoformat(timespec="seconds")
    assert snapshot.next_refresh_at == expected_refresh


def test_credit_parser_refuses_wrong_account():
    with pytest.raises(PermissionError, match="not authenticated"):
        parse_credit_snapshot(
            "0 Google Flow credits\nCredits refresh daily at 7:41 PM",
            "infolillylooks@gmail.com",
        )


def test_credit_parser_refuses_unverified_balance():
    with pytest.raises(ValueError, match="Could not verify"):
        parse_credit_snapshot(
            "infolillylooks@gmail.com\nCredits refresh daily at 7:41 PM",
            "infolillylooks@gmail.com",
        )


def test_next_refresh_moves_to_tomorrow_after_daily_refresh_time():
    local_timezone = datetime.now().astimezone().tzinfo
    now = datetime(2026, 10, 7, 20, 0, tzinfo=local_timezone)
    snapshot = parse_credit_snapshot(
        "infolillylooks@gmail.com\n"
        "0 Google Flow credits\nCredits refresh daily at 7:41 PM",
        "infolillylooks@gmail.com",
        now=now,
    )

    assert snapshot.next_refresh_at == now.replace(
        day=8,
        hour=19,
        minute=41,
    ).isoformat(timespec="seconds")


def test_generation_claim_skips_pending_scenes_for_terminal_or_stale_stories(tmp_path):
    db = DatabaseManager(str(tmp_path / "engine.db"))
    with db.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO accounts (id, slot_index, email, tier, status, available_credits)
            VALUES ('acc_4', 4, 'infolillylooks@gmail.com', 'FREE', 'ACTIVE', 50)
            """
        )
        for story_id, story_state in (
            ("published", "PUBLISHED"),
            ("completed", "COMPLETED"),
            ("stale_generating", "GENERATING"),
            ("eligible_partial", "PARTIAL"),
        ):
            conn.execute(
                """
                INSERT INTO stories
                    (id, title, concept_summary, structure_type, story_hash, state)
                VALUES (?, ?, 'test', 'test', ?, ?)
                """,
                (story_id, story_id, story_id, story_state),
            )
            conn.execute(
                """
                INSERT INTO story_parts
                    (id, story_id, part_number, scene_label, prompt_text, prompt_hash, status)
                VALUES (?, ?, 1, 'scene', 'prompt', ?, 'PENDING')
                """,
                (f"{story_id}_part", story_id, f"{story_id}_hash"),
            )

    engine = MultiAccountParallelEngine.__new__(MultiAccountParallelEngine)
    engine._lock = threading.Lock()
    engine.db = db
    engine.duplicate_agent = _NoDuplicate()

    claimed = engine.claim_next_work_item(4)

    assert claimed["id"] == "eligible_partial_part"
    with db.get_connection() as conn:
        states = {
            row["id"]: row["status"]
            for row in conn.execute(
                "SELECT id, status FROM story_parts ORDER BY id"
            )
        }
    assert states["published_part"] == "PENDING"
    assert states["completed_part"] == "PENDING"
    assert states["stale_generating_part"] == "PENDING"


def test_tiktok_parser_reads_visible_studio_row_when_table_selector_is_empty():
    text = """Posts 99
01:04
Dino ne chheenk diya! #dinosaur
7 Oct, 12:48 pm
Public
65
2
1"""

    posts = parse_tiktok_raw_page(text)

    assert posts == [{
        "title": "Dino ne chheenk diya! #dinosaur",
        "caption": "Dino ne chheenk diya! #dinosaur",
        "duration_seconds": 64,
        "published_at": "7 Oct, 12:48 pm",
        "views": 65,
        "likes": 2,
        "comments": 1,
        "visibility": "Public",
    }]


def test_doctor_marks_metrics_missing_instead_of_inventing_reach_causes():
    doctor = ChannelDoctorAgent("@sample", "@sample_tiktok")

    report = doctor.diagnose()

    assert report["overall_assessment"] == "INSUFFICIENT_CURRENT_ANALYTICS"
    assert any(
        finding["id"] == "YOUTUBE_ANALYTICS_MISSING"
        and finding["evidence_type"] == "hypothesis"
        for finding in report["findings"]
    )
    assert report["scope"]["publishing_or_deleting_performed"] is False


def test_doctor_flags_observable_tiktok_posting_burst_without_claiming_causality():
    doctor = ChannelDoctorAgent("@sample", "@sample_tiktok")
    posts = [
        {"published_at": "7 Oct, 12:08 pm", "views": 148, "duration_seconds": 52},
        {"published_at": "7 Oct, 12:35 pm", "views": 106, "duration_seconds": 64},
        {"published_at": "7 Oct, 12:40 pm", "views": 76, "duration_seconds": 62},
        {"published_at": "7 Oct, 12:44 pm", "views": 59, "duration_seconds": 64},
        {"published_at": "7 Oct, 12:48 pm", "views": 65, "duration_seconds": 64},
    ]

    report = doctor.diagnose(
        studio_export={"tiktok": {"as_of": "2026-10-07T13:00:00+01:00", "videos": posts}},
        now=datetime.fromisoformat("2026-10-07T14:00:00+01:00"),
    )
    burst = next(f for f in report["findings"] if f["id"] == "TIKTOK_POSTING_BURST")

    assert "5 posts" in burst["summary"]
    assert "unproven" in burst["summary"]


def test_doctor_compares_youtube_retention_within_own_top_content():
    doctor = ChannelDoctorAgent("@sample", "@sample_tiktok")
    videos = [
        {"title": "Most viewed", "views": 1900, "duration_seconds": 25, "average_percentage_viewed": 17.1},
        {"title": "Second", "views": 980, "duration_seconds": 24, "average_percentage_viewed": 78.0},
        {"title": "Third", "views": 900, "duration_seconds": 24, "average_percentage_viewed": 39.6},
        {"title": "Low views replay", "views": 37, "duration_seconds": 19, "average_percentage_viewed": 172.9},
    ]

    report = doctor.diagnose(
        studio_export={
            "youtube": {
                "as_of": "2026-10-07T12:00:00+01:00",
                "channel": {"views_last_28_days": 4711, "watch_hours_last_28_days": 13.8},
                "videos": videos,
            }
        },
        now=datetime.fromisoformat("2026-10-07T14:00:00+01:00"),
    )
    finding = next(item for item in report["findings"] if item["id"] == "YOUTUBE_RETENTION_SPREAD")

    assert "17.1% to 78%" in finding["summary"]
    assert "Most viewed" in finding["recommended_action"][1]
    concentration = next(
        item for item in report["findings"]
        if item["id"] == "YOUTUBE_TOP_CONTENT_CONCENTRATION"
    )
    assert "80%" in concentration["summary"]
