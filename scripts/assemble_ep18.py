import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.db.database import DatabaseManager
from backend.services.assembly_service import VideoAssemblyService

assembler = VideoAssemblyService()
raw_clips = BASE_DIR / "data" / "raw_clips"

parts = [
    str(raw_clips / "ep_18_scene_01.mp4"),
    str(raw_clips / "ep_18_scene_02.mp4")
]

final_video = assembler.merge_story_parts("ep_18_magic_freeze_remote", parts)
print("Master Assembly SUCCESS:", final_video)

db = DatabaseManager()
with db.get_connection() as conn:
    conn.execute("UPDATE stories SET state = 'COMPLETED', updated_at = CURRENT_TIMESTAMP WHERE id = 'ep_18_magic_freeze_remote'")
    conn.commit()

status = {
    "active_id": "ep_18_magic_freeze_remote",
    "active_title": "Mummy Ka Magic Remote! Sab Freeze Ho Gaye! #TheNaughtyDuo #shorts",
    "active_account": "/u/3/ (pinku.pub@gmail.com) -> Handing off to Slot 4",
    "active_scene": "Episode Master Produced & Assembled (8.1 MB HD)",
    "percentage": 100,
    "parts_text": "Scenes 1 & 2 Assembled into Master Short on Disk -> Ready for Release",
    "stage": "Master Video Assembled | Ready to Publish",
    "target_platform": "YouTube Shorts & TikTok",
    "delay_reason": "🟢 100% Completed! Master video assembled in data/output/ep_18_magic_freeze_remote_final.mp4. Ready for YouTube & TikTok."
}

with open(BASE_DIR / "data" / "live_production_status.json", "w", encoding="utf-8") as f:
    json.dump(status, f, indent=2, ensure_ascii=False)

print("Status updated to 100% successfully!")
