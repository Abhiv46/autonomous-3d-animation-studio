import pytest

from platforms.youtube.youtube_adapter import YouTubePlatformAdapter


class FakeRequest:
    def __init__(self, result=None):
        self.result = result or {}
        self.called = False

    def execute(self):
        self.called = True
        return self.result


class FakeVideos:
    def __init__(self, video):
        self.video = video
        self.updated = None
        self.deleted = None

    def list(self, **kwargs):
        return FakeRequest({"items": [self.video]})

    def update(self, **kwargs):
        self.updated = kwargs
        return FakeRequest({"id": self.video["id"], "snippet": kwargs["body"]["snippet"]})

    def delete(self, **kwargs):
        self.deleted = kwargs
        return FakeRequest()


class FakeService:
    def __init__(self, video):
        self.video_service = FakeVideos(video)

    def videos(self):
        return self.video_service


def test_metadata_update_dry_run_checks_owned_channel_and_live_title(tmp_path, monkeypatch):
    monkeypatch.setenv("LIVE_PUBLISH_APPROVED", "true")
    adapter = YouTubePlatformAdapter(str(tmp_path / "token"), "channel")
    adapter.service = FakeService(
        {
            "id": "abcdefghijk",
            "snippet": {
                "channelId": "channel",
                "title": "Old title",
                "description": "Old description",
                "categoryId": "22",
            },
        }
    )

    result = adapter.update_video_metadata(
        "abcdefghijk",
        "Old title",
        {"title": "New title"},
        dry_run=True,
    )

    assert result["status"] == "DRY_RUN_ONLY"
    assert adapter.service.video_service.updated is None


def test_metadata_update_blocks_channel_mismatch(tmp_path, monkeypatch):
    monkeypatch.setenv("LIVE_PUBLISH_APPROVED", "true")
    adapter = YouTubePlatformAdapter(str(tmp_path / "token"), "channel")
    adapter.service = FakeService(
        {"id": "abcdefghijk", "snippet": {"channelId": "other", "title": "Old title"}}
    )

    with pytest.raises(PermissionError, match="does not belong"):
        adapter.update_video_metadata(
            "abcdefghijk",
            "Old title",
            {"title": "New title"},
            dry_run=True,
        )


def test_delete_respects_protected_video_ids(tmp_path, monkeypatch):
    monkeypatch.setenv("LIVE_PUBLISH_APPROVED", "true")
    adapter = YouTubePlatformAdapter(
        str(tmp_path / "token"),
        "channel",
        protected_video_ids=["abcdefghijk"],
    )
    adapter.service = FakeService(
        {"id": "abcdefghijk", "snippet": {"channelId": "channel", "title": "Protected"}}
    )

    with pytest.raises(PermissionError, match="protected"):
        adapter.delete_video(
            "abcdefghijk",
            "Protected",
            "DELETE youtube abcdefghijk",
            "verified_duplicate",
            "evidence-123",
            dry_run=True,
        )
    assert adapter.service.video_service.deleted is None
