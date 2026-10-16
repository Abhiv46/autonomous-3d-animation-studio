from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from agents.quality_control.quality_agent import QualityAssuranceAgent
from agents.seo.seo_agent import ViralSchedulingAgent


def test_quality_assurance_agent_flags_missing_cta():
    agent = QualityAssuranceAgent()
    report = agent.assess_story_bundle({
        "title": "Test Story",
        "prompt": "Kaavya Kaartik Pinki in a room",
        "flow_story": {"scene_sequence": [1, 2, 3, 4, 5, 6, 7, 8]},
        "script": {"duration_seconds": 60},
        "publishing_payload": {"video_path": "./tmp/does_not_exist.mp4"},
    })
    assert report["passed"] is False
    assert "MISSING_CTA" in report["issues"] or "VIDEO_FILE_NOT_FOUND" in report["issues"]


def test_viral_scheduler_provides_prime_slots():
    agent = ViralSchedulingAgent({
        "platforms": {
            "youtube": {"prime_slots_ist": ["09:00", "11:30", "14:00"]},
            "tiktok": {"prime_slots_ist": ["13:00", "17:30", "20:30"]},
        }
    })
    youtube_slot = agent.choose_best_slot("youtube")
    tiktok_slot = agent.choose_best_slot("tiktok")
    assert youtube_slot["slot_ist"] == "09:00"
    assert tiktok_slot["slot_ist"] == "13:00"
