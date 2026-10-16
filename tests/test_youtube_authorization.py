import pytest

from scripts.authorize_youtube import verify_authorized_channel


class FakeChannels:
    def __init__(self, items):
        self.items = items

    def list(self, **kwargs):
        return self

    def execute(self):
        return {"items": self.items}


class FakeService:
    def __init__(self, items):
        self.items = items

    def channels(self):
        return FakeChannels(self.items)


def test_authorized_channel_must_match_target_before_token_save():
    channel = verify_authorized_channel(
        FakeService([{"id": "expected-channel", "snippet": {"title": "Target"}}]),
        "expected-channel",
    )

    assert channel == {
        "channel_id": "expected-channel",
        "channel_title": "Target",
    }


def test_authorization_refuses_different_channel():
    with pytest.raises(PermissionError, match="does not own"):
        verify_authorized_channel(
            FakeService([{"id": "other-channel"}]),
            "expected-channel",
        )


def test_authorization_refuses_ambiguous_channel_selection():
    with pytest.raises(PermissionError, match="expected exactly one"):
        verify_authorized_channel(
            FakeService([{"id": "one"}, {"id": "two"}]),
            "expected-channel",
        )
