import json
import sqlite3
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(r"C:\TheNaughtyDuo_Automation\uploaded_videos_log.json")
DB_FILE = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\content_engine.db")

now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
new_url = "https://youtube.com/shorts/tAOBfQ70naM"
title = "Mummy Ka Magic Remote! 🎮😂 Sab Freeze Ho Gaye! #TheNaughtyDuo #shorts"

# 1. Update uploaded_videos_log.json
if LOG_FILE.exists():
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Append the new authentic live video
    data.setdefault("uploaded", []).append({
        "key": "ep_18_magic_freeze_remote",
        "filename": "ep_18_magic_freeze_remote_final.mp4",
        "size_mb": 9.23,
        "youtube": new_url,
        "youtube_title": title,
        "youtube_status": "LIVE",
        "timestamp": now_str
    })
    
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("[+] uploaded_videos_log.json updated!")

# 2. Update content_engine.db
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

c.execute("UPDATE stories SET state = 'PUBLISHED', updated_at = ? WHERE id = 'ep_18_magic_freeze_remote'", (now_str,))
c.execute("""
    UPDATE publishing_jobs
    SET status = 'PUBLISHED', platform_url = ?, published_at = ?
    WHERE story_id = 'ep_18_magic_freeze_remote' AND platform = 'YOUTUBE'
""", (new_url, now_str))

conn.commit()
conn.close()
print("[+] content_engine.db updated with PUBLISHED state and live link!")
