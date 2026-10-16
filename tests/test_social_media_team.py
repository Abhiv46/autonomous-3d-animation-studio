from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from agents.social_media_team.agent_team import ResearchAgent, SocialMediaAgentTeam


def test_research_agent_builds_content_ideas():
    agent = ResearchAgent()
    ideas = agent.generate_ideas(limit=3)
    assert len(ideas) == 3
    assert all("title" in idea and "hook" in idea for idea in ideas)
    assert all("idea-" in idea["id"] for idea in ideas)


def test_daily_batch_generates_account_and_platform_plan():
    team = SocialMediaAgentTeam(config_path=BASE_DIR / "config" / "config.json")
    batch = team.plan_daily_batch(max_videos=2)
    assert len(batch) == 2
    assert {item["platform"] for item in batch} <= {"youtube", "tiktok"}
    assert {item["account"]["slot_index"] for item in batch} == {0, 1}
    assert all(item["script"]["duration_seconds"] >= 45 for item in batch)


def test_publishing_validation_enforces_platform_rules():
    team = SocialMediaAgentTeam(config_path=BASE_DIR / "config" / "config.json")
    valid = team.publisher_agent.validate_publication_payload({
        "platform": "youtube",
        "channel_id": team.config["platforms"]["youtube"]["channel_id"],
        "video_path": "./tmp/sample.mp4",
        "duration_seconds": 60,
    })
    assert valid["valid"] is True

    invalid = team.publisher_agent.validate_publication_payload({
        "platform": "tiktok",
        "channel_id": "TIKTOK_STUDIO",
        "video_path": "./tmp/sample.mp4",
        "duration_seconds": 30,
    })
    assert invalid["valid"] is False
    assert "TIKTOK_POLICY" in invalid["error"]


def test_live_cycle_stays_safe_without_video_files():
    team = SocialMediaAgentTeam(config_path=BASE_DIR / "config" / "config.json")
    summary = team.run_daily_cycle(max_videos=1, live_mode=True, dry_run=True)
    assert summary["batch_size"] == 1
    assert summary["items"][0]["upload_status"] == "BLOCKED_QA"
    assert summary["items"][0]["job_state"] == "blocked"
    assert summary["agent_dashboard"]["live_upload_ready"] is False


def test_dry_run_never_claims_content_was_published():
    team = SocialMediaAgentTeam(config_path=BASE_DIR / "config" / "config.json")
    batch = team.plan_daily_batch(max_videos=1)
    quality_results = team.quality_agent.evaluate_batch(batch)
    result = team.publish_batch(batch, live_mode=False, dry_run=True, quality_results=quality_results)

    assert result[0]["status"] != "SIMULATED_POSTED"
    assert result[0]["status"] == "BLOCKED_QA"


def test_live_cycle_requires_live_gate_approval(monkeypatch):
    team = SocialMediaAgentTeam(config_path=BASE_DIR / "config" / "config.json")
    monkeypatch.setattr(
        team.live_gate,
        "inspect",
        lambda: {"ready": False, "reasons": ["test approval is missing"]},
    )
    try:
        team.run_daily_cycle(max_videos=1, live_mode=True, dry_run=False)
    except PermissionError as exc:
        assert "Live publishing is blocked" in str(exc)
    else:
        raise AssertionError("Live cycle must be blocked without valid approval and credentials")


def test_analytics_agent_does_not_score_missing_metrics_as_zero():
    team = SocialMediaAgentTeam(config_path=BASE_DIR / "config" / "config.json")

    result = team.analytics_agent.score_video({"views": 0})

    assert result["available"] is False
    assert result["score"] is None
    assert result["recommendation"] == "collect_analytics"
    assert "retention_rate" in result["missing_metrics"]
