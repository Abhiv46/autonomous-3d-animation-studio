from agents.channel_doctor.action_executor import ChannelDoctorActionExecutor
import pytest


def _config():
    return {
        "platforms": {
            "youtube": {
                "enabled": True,
                "channel_id": "channel-id",
                "protected_videos": ["protect0001"],
            },
            "tiktok": {
                "enabled": True,
                "channel_handle": "@thenaughtyduoofficial",
            },
        }
    }


def test_action_plan_dry_run_does_not_apply_live_changes(tmp_path, monkeypatch):
    monkeypatch.setenv("LIVE_PUBLISH_APPROVED", "true")
    executor = ChannelDoctorActionExecutor(_config(), tmp_path)
    plan = {
        "actions": [
            {
                "platform": "tiktok",
                "operation": "update_caption",
                "video_id": "7693972591236648214",
                "expected_title": "Existing caption",
                "metadata": {"caption": "Proposed caption"},
            }
        ]
    }

    result = executor.execute(plan, dry_run=True)

    assert result["mode"] == "dry_run"
    assert result["live_actions_performed"] is False
    assert result["results"][0]["status"] == "BLOCKED"
    assert "does not expose" in result["results"][0]["reason"]


def test_deletion_requires_verified_evidence_and_exact_confirmation(tmp_path, monkeypatch):
    monkeypatch.setenv("LIVE_PUBLISH_APPROVED", "true")
    executor = ChannelDoctorActionExecutor(_config(), tmp_path)
    action = {
        "platform": "tiktok",
        "operation": "delete",
        "video_id": "7693972591236648214",
        "expected_title": "Exact caption",
        "reason_type": "possible_duplicate",
        "evidence_reference": "title-match",
        "confirmation": "DELETE tiktok 7693972591236648214",
    }

    result = executor.execute({"actions": [action]}, dry_run=True)

    assert result["results"][0]["status"] == "BLOCKED"
    assert "verified duplicate or official platform policy notice" in result["results"][0]["reason"]


def test_deletion_plan_is_validated_before_any_platform_access(tmp_path, monkeypatch):
    monkeypatch.setenv("LIVE_PUBLISH_APPROVED", "true")
    executor = ChannelDoctorActionExecutor(_config(), tmp_path)
    action = {
        "platform": "youtube",
        "operation": "delete",
        "video_id": "protect0001",
        "expected_title": "Protected",
        "reason_type": "official_policy_notice",
        "evidence_reference": "notice-123",
        "confirmation": "DELETE youtube protect0001",
    }

    result = executor.execute({"actions": [action]}, dry_run=True)

    assert result["results"][0]["status"] == "BLOCKED"
    assert "protected" in result["results"][0]["reason"]


def test_action_plan_rejects_missing_actions_array(tmp_path):
    executor = ChannelDoctorActionExecutor(_config(), tmp_path)

    try:
        executor.execute({}, dry_run=True)
    except ValueError as error:
        assert "actions list" in str(error)
    else:
        raise AssertionError("Action plans without an actions array must be rejected.")


def test_verified_duplicate_requires_identical_local_source_fingerprints(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("LIVE_PUBLISH_APPROVED", "true")
    original = tmp_path / "original.mp4"
    duplicate = tmp_path / "duplicate.mp4"
    original.write_bytes(b"same video bytes")
    duplicate.write_bytes(b"same video bytes")
    executor = ChannelDoctorActionExecutor(_config(), tmp_path)
    action = {
        "platform": "tiktok",
        "operation": "delete",
        "video_id": "7693972591236648214",
        "expected_title": "Duplicate post",
        "reason_type": "verified_duplicate",
        "evidence_reference": "local source fingerprint comparison",
        "duplicate_video_id": "7693972591236648215",
        "duplicate_expected_title": "Original post",
        "source_path": str(original),
        "duplicate_source_path": str(duplicate),
        "confirmation": "DELETE tiktok 7693972591236648214",
    }

    executor._validate_action(action, dry_run=True)

    duplicate.write_bytes(b"different video bytes")
    with pytest.raises(ValueError, match="identical SHA-256"):
        executor._validate_action(action, dry_run=True)


def test_delete_requires_exact_confirmation_even_with_official_notice(tmp_path, monkeypatch):
    monkeypatch.setenv("LIVE_PUBLISH_APPROVED", "true")
    executor = ChannelDoctorActionExecutor(_config(), tmp_path)
    action = {
        "platform": "youtube",
        "operation": "delete",
        "video_id": "abcdefghijk",
        "expected_title": "Risky video",
        "reason_type": "official_policy_notice",
        "evidence_reference": "notice-123",
        "confirmation": "DELETE youtube anotherid",
    }

    with pytest.raises(PermissionError, match="exact platform"):
        executor._validate_action(action, dry_run=True)
