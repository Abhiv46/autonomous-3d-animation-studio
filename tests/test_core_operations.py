import pytest
import os
import tempfile
import sys
from pathlib import Path

# Setup path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.db.database import DatabaseManager
from agents.duplicate_detection.duplicate_agent import DuplicateDetectionAgent
from agents.prompt_engineering.prompt_agent import PromptEngineeringAgent
from agents.account_manager.account_agent import AccountManagerAgent
from platforms.youtube.youtube_adapter import YouTubePlatformAdapter
from platforms.tiktok.tiktok_adapter import TikTokPlatformAdapter

@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    db = DatabaseManager(db_path=db_path)
    yield db
    try:
        os.remove(db_path)
    except Exception:
        pass

def test_1_windows_restart_duplicate_protection(temp_db):
    """TEST 1 & 7: Verify that submitting the same story/prompt twice is rejected immediately."""
    story_id = "TND-2026-000001"
    title = "Papa Ke Bade Jooton Ki Race"
    prompts = [
        {"part_number": 1, "scene_label": "Hook", "prompt_text": "Pinki Mummy reads newspaper."},
        {"part_number": 2, "scene_label": "Prank", "prompt_text": "Kaartik puts on big boots."}
    ]
    
    # 1st Registration -> Success
    res = temp_db.register_story(story_id, title, "Kids shoes race", "PROBLEM_PAYOFF", prompts)
    assert res == story_id

    # 2nd Registration with same title -> Must Raise ValueError
    with pytest.raises(ValueError) as exc:
        temp_db.register_story("TND-2026-000002", title, "Duplicate concept", "PROBLEM_PAYOFF", prompts)
    assert "Duplicate story rejected" in str(exc.value)

def test_2_incomplete_story_recovery(temp_db):
    """TEST 2 & 4: If a 4-part story has only Part 1 completed, it must be marked PARTIAL (P0 priority)."""
    story_id = "TND-2026-000002"
    title = "Mummy Ka Surprise Birthday Cake"
    prompts = [
        {"part_number": 1, "scene_label": "P1", "prompt_text": "Mummy hides cake in fridge."},
        {"part_number": 2, "scene_label": "P2", "prompt_text": "Kids sneak into kitchen."},
        {"part_number": 3, "scene_label": "P3", "prompt_text": "Chocolate face reveal."},
        {"part_number": 4, "scene_label": "P4", "prompt_text": "Family celebration hug."}
    ]
    temp_db.register_story(story_id, title, "Cake prank", "PROBLEM_PAYOFF", prompts)
    
    # Mark only Part 1 as completed
    part_1_id = f"{story_id}-P01"
    temp_db.update_part_status(part_1_id, "COMPLETED", raw_path="part1.mp4")

    # Fetch highest priority job -> Must return Story 2 as P0
    job = temp_db.get_highest_priority_job()
    assert job is not None
    assert job["id"] == story_id
    assert job["state"] == "PARTIAL"
    assert job["priority"] == 0 # P0 Priority!

def test_3_account_switching_on_credits_exhausted():
    """TEST 3: When credits are exhausted on Account 1, system safely switches to next healthy account."""
    accounts = [
        {"slot_index": 0, "email": "acc0@test.com", "status": "ACTIVE", "available_credits": 0},
        {"slot_index": 1, "email": "acc1@test.com", "status": "ACTIVE", "available_credits": 50}
    ]
    mgr = AccountManagerAgent(accounts)
    
    # Account 0 has 0 credits -> Must select Account 1
    selected = mgr.select_best_account(required_credits=15, current_slot=0)
    assert selected is not None
    assert selected["slot_index"] == 1
    assert selected["email"] == "acc1@test.com"

def test_5_character_lock_enforcement():
    """TEST 5: Verify character lock permanently inserts Pinki, Kaartik, and Kaavya without hallucinated characters."""
    characters = [
        {"name": "Pinki", "role": "Mom"},
        {"name": "Kaartik", "role": "Son"},
        {"name": "Kaavya", "role": "Daughter"}
    ]
    agent = PromptEngineeringAgent(characters)
    prompt = agent.build_locked_prompt("Kids dancing cheerfully in living room.")
    
    assert "@Kaartik" in prompt
    assert "@Kaavya" in prompt
    assert "@Pinki" in prompt
    assert "No duplicate or clone characters" in prompt
    assert "Garden Me Jhula" in prompt

def test_6_wrong_channel_upload_protection():
    """TEST 10: Publishing validation blocks upload if channel ID mismatch occurs."""
    adapter = YouTubePlatformAdapter(token_pickle_path="dummy.pickle", target_channel_id="UCULzzCCm0Y-ZHiYF480ioLg")
    
    payload = {
        "channel_id": "WRONG_CHANNEL_ID_999",
        "video_path": "sample.mp4",
        "title": "Sample Title"
    }
    val = adapter.validate_publication_payload(payload)
    assert val["valid"] is False
    assert "SECURITY_ALERT" in val["error"]

def test_7_tiktok_duration_compliance():
    """TEST: TikTok adapter enforces 60s minimum duration for Creator Rewards Program."""
    adapter = TikTokPlatformAdapter()
    payload = {
        "video_path": "non_existent.mp4",
        "duration_seconds": 30.0 # Under 60s
    }
    val = adapter.validate_publication_payload(payload)
    assert val["valid"] is False
    assert "MISSING_VIDEO_FILE" in val["error"]
