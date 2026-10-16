from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from agents.google_flow.google_flow_agent import GoogleFlowGenerationAgent


def test_google_flow_agent_builds_locked_story_pack():
    agent = GoogleFlowGenerationAgent()
    pack = agent.build_default_waterpark_story()

    assert pack["title"]
    assert pack["scene_sequence"][0]["scene_number"] == 1
    assert pack["scene_sequence"][-1]["scene_number"] == 8
    assert "Kaavya" in pack["character_lock"]
    assert "Kaartik" in pack["character_lock"]
    assert "Pinki" in pack["character_lock"]
    assert "9:16" in pack["aspect_ratio"]
    assert "no deep water" in pack["negative_prompt"]


def test_generate_daily_prompt_pack_for_custom_story():
    agent = GoogleFlowGenerationAgent()
    scenes = [
        {"scene_number": 1, "title": "Hook", "description": "Surprise reveal", "dialogue": "Mummy!", "duration_seconds": 8},
        {"scene_number": 2, "title": "Climax", "description": "Funny chase", "dialogue": "Run!", "duration_seconds": 8},
    ]
    pack = agent.generate_daily_prompt_pack("Daily Funny Story", "A tiny chaos at home", scenes)
    assert len(pack["scene_sequence"]) == 2
    assert "Daily Funny Story" in pack["title"]
    assert "Scene 1" in pack["scene_sequence"][0]["prompt"] or "Scene 1" in pack["scene_sequence"][0]["title"]
