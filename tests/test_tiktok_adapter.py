from scripts.tiktok_studio_uploader import (
    _normalize_visible_text,
    tiktok_identity_matches,
    upload_to_tiktok_studio,
)
from platforms.tiktok.tiktok_adapter import TikTokPlatformAdapter


def test_tiktok_account_identity_requires_exact_handle_match():
    assert tiktok_identity_matches(
        "@family.fun",
        ["https://www.tiktok.com/@family.fun"],
        "",
    )
    assert tiktok_identity_matches("@family.fun", [], "Signed in as @family.fun")
    assert not tiktok_identity_matches(
        "@family.fun",
        ["https://www.tiktok.com/@family.funny"],
        "Signed in as @family.funny",
    )
    assert not tiktok_identity_matches("", ["https://www.tiktok.com/@family.fun"], "")


def test_tiktok_caption_comparison_ignores_harmless_unicode_spacing():
    assert _normalize_visible_text("A\u00a0\u200b B") == _normalize_visible_text("A B")


def test_tiktok_live_upload_requires_configured_handle_and_approval(tmp_path, monkeypatch):
    video_path = tmp_path / "sample.mp4"
    video_path.write_bytes(b"test")
    monkeypatch.delenv("LIVE_PUBLISH_APPROVED", raising=False)
    monkeypatch.setenv("LIVE_APPROVAL_FILE", str(tmp_path / "missing-approval.txt"))

    missing_handle = upload_to_tiktok_studio(
        str(video_path),
        "caption",
        dry_run=False,
    )
    unapproved = upload_to_tiktok_studio(
        str(video_path),
        "caption",
        expected_handle="@family.fun",
        dry_run=False,
    )

    assert missing_handle["status"] == "TIKTOK_HANDLE_NOT_CONFIGURED"
    assert unapproved["status"] == "LIVE_PUBLISH_NOT_APPROVED"


def test_tiktok_adapter_does_not_claim_authentication_without_target_handle():
    assert TikTokPlatformAdapter().authenticate() is False


def test_persisted_approval_is_honored_for_tiktok_live_gate(tmp_path, monkeypatch):
    approval_path = tmp_path / "approved.txt"
    approval_path.write_text("approved\n", encoding="utf-8")
    monkeypatch.delenv("LIVE_PUBLISH_APPROVED", raising=False)
    monkeypatch.setenv("LIVE_APPROVAL_FILE", str(approval_path))

    from platforms.live_production import LiveProductionGate

    assert LiveProductionGate().is_approved()


def test_tiktok_adapter_dry_run_never_reports_a_published_post(tmp_path, monkeypatch):
    video_path = tmp_path / "sample.mp4"
    video_path.write_bytes(b"test")
    monkeypatch.setenv("DRY_RUN", "true")

    result = TikTokPlatformAdapter("@thenaughtyduoofficial").upload_short(
        str(video_path),
        {"caption": "test"},
    )

    assert result == {"success": False, "status": "DRY_RUN_ONLY"}
