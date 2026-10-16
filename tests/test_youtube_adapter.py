import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from platforms.youtube.youtube_adapter import YouTubePlatformAdapter

def test_youtube_adapter_init():
    adapter = YouTubePlatformAdapter("dummy_token.pickle", "dummy_channel_id")
    assert adapter.target_channel_id == "dummy_channel_id"
    assert adapter.token_pickle_path == "dummy_token.pickle"


def test_unconfigured_analytics_are_not_reported_as_zero():
    adapter = YouTubePlatformAdapter("dummy_token.pickle", "dummy_channel_id")

    result = adapter.get_analytics("video-id")

    assert result["available"] is False
    assert "not configured" in result["reason"]
    assert "views" not in result
