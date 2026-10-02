import os
import re
import json
import glob
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
from backend.db.database import DatabaseManager

logger = logging.getLogger("CrossPlatformScanner")

class CrossPlatformScanner:
    """Permanently scans YouTube channel, scheduled queues, and TikTok studio history
    to build a live zero-tolerance index preventing duplicate video production."""

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db if db else DatabaseManager()
        self.automation_dir = Path("C:/TheNaughtyDuo_Automation")

    @staticmethod
    def normalize_text(text: str) -> str:
        """Strips emojis, special characters, and extra spaces for exact matching."""
        clean = re.sub(r"[^a-zA-Z0-9\s]", "", text.lower())
        return " ".join(clean.split())

    @staticmethod
    def extract_concept_keywords(text: str) -> List[str]:
        """Extracts significant subject, prank, and concept keywords (ignoring generic stop words)."""
        stop_words = {
            "the", "naughty", "duo", "shorts", "hindi", "cartoon", "video", "ep", "episode",
            "mummy", "kaartik", "kaavya", "pinki", "aur", "ka", "ki", "ke", "me", "se", "ko",
            "par", "hai", "ye", "kya", "bana", "gaya", "gaye", "wale", "wala", "full", "hd", "3d",
            "ghar", "aaya", "aayi", "gayi", "hoga", "hogi", "karein", "karo", "rahe", "rahi",
            "raha", "thi", "tha", "the", "ek", "do", "sab", "naya", "nayi", "bhi", "toh", "jab", "tab", "ab"
        }
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        return [w for w in words if w not in stop_words]

    def scan_youtube(self) -> int:
        """Scans YouTube channel registry, scheduled queues, and config benchmarks."""
        count = 0
        records = []

        # 1. Scan channel_existing_videos.json
        ch_file = self.automation_dir / "channel_existing_videos.json"
        if ch_file.exists():
            try:
                with open(ch_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for item in data:
                    title = item.get("title", "")
                    if title:
                        records.append({
                            "id": f"yt_{item.get('id', title[:20])}",
                            "platform": "YOUTUBE",
                            "title": title,
                            "normalized": self.normalize_text(title),
                            "keywords": ",".join(self.extract_concept_keywords(title)),
                            "source": "CHANNEL_HISTORY",
                            "status": item.get("status", "PUBLISHED")
                        })
            except Exception as e:
                logger.error(f"[SCANNER] Error reading channel_existing_videos: {e}")

        # 2. Scan schedule_slots.json
        slots_file = self.automation_dir / "schedule_slots.json"
        if slots_file.exists():
            try:
                with open(slots_file, "r", encoding="utf-8") as f:
                    slots = json.load(f)
                for s in slots:
                    title = s.get("title", "")
                    if title:
                        records.append({
                            "id": f"yt_sched_{s.get('slot', title[:15])}",
                            "platform": "YOUTUBE",
                            "title": title,
                            "normalized": self.normalize_text(title),
                            "keywords": ",".join(self.extract_concept_keywords(title)),
                            "source": "SCHEDULE_QUEUE",
                            "status": "SCHEDULED"
                        })
            except Exception as e:
                logger.error(f"[SCANNER] Error reading schedule_slots: {e}")

        # 3. Scan uploaded_videos_log.json
        up_file = self.automation_dir / "uploaded_videos_log.json"
        if up_file.exists():
            try:
                with open(up_file, "r", encoding="utf-8") as f:
                    up_data = json.load(f)
                for item in up_data.get("uploaded", []):
                    title = item.get("youtube_title") or item.get("title") or item.get("filename") or ""
                    link = item.get("youtube") or item.get("link") or ""
                    if link and link.startswith("http"):
                        records.append({
                            "id": f"yt_log_{item.get('key', title[:15])}",
                            "platform": "YOUTUBE",
                            "title": title or item.get("key"),
                            "normalized": self.normalize_text(title or item.get("key")),
                            "keywords": ",".join(self.extract_concept_keywords(title or item.get("key"))),
                            "source": "UPLOAD_LOG",
                            "status": "PUBLISHED"
                        })
            except Exception as e:
                logger.error(f"[SCANNER] Error reading uploaded_videos_log: {e}")

        # Insert records into SQLite
        with self.db.get_connection() as conn:
            for r in records:
                conn.execute("""
                    INSERT OR REPLACE INTO platform_indexed_videos 
                    (id, platform, title, normalized_title, keywords, source_type, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (r["id"], r["platform"], r["title"], r["normalized"], r["keywords"], r["source"], r["status"]))
                count += 1

        logger.info(f"[SCANNER] YouTube scan complete: Indexed {count} active/scheduled videos.")
        return count

    def scan_tiktok(self) -> int:
        """Scans TikTok studio posted proofs, filenames, and staged videos."""
        count = 0
        records = []
        out_dir = self.automation_dir / "output"

        if out_dir.exists():
            # Scan tt_posted screenshots (direct proof of upload)
            for f in glob.glob(str(out_dir / "tt_posted_*.png")):
                base = os.path.basename(f).replace("tt_posted_", "").replace(".mp4.png", "").replace(".png", "")
                title_guess = base.replace("_", " ").title()
                records.append({
                    "id": f"tt_{base[:30]}",
                    "platform": "TIKTOK",
                    "title": title_guess,
                    "normalized": self.normalize_text(title_guess),
                    "keywords": ",".join(self.extract_concept_keywords(title_guess)),
                    "source": "STUDIO_POSTED",
                    "status": "PUBLISHED"
                })

            # Scan TikTok video files
            for vid in glob.glob(str(out_dir / "*TikTok*.mp4")):
                base = os.path.basename(vid).replace(".mp4", "").replace("TheNaughtyDuo_", "")
                title_guess = base.replace("_", " ").title()
                records.append({
                    "id": f"tt_vid_{base[:30]}",
                    "platform": "TIKTOK",
                    "title": title_guess,
                    "normalized": self.normalize_text(title_guess),
                    "keywords": ",".join(self.extract_concept_keywords(title_guess)),
                    "source": "STUDIO_POSTED",
                    "status": "PUBLISHED"
                })

        with self.db.get_connection() as conn:
            for r in records:
                conn.execute("""
                    INSERT OR REPLACE INTO platform_indexed_videos 
                    (id, platform, title, normalized_title, keywords, source_type, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (r["id"], r["platform"], r["title"], r["normalized"], r["keywords"], r["source"], r["status"]))
                count += 1

        logger.info(f"[SCANNER] TikTok scan complete: Indexed {count} posted videos.")
        return count

    def sync_all_platforms(self) -> Dict[str, Any]:
        """Runs complete deep scan of both YouTube and TikTok."""
        yt_count = self.scan_youtube()
        tt_count = self.scan_tiktok()
        with self.db.get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) as c FROM platform_indexed_videos").fetchone()["c"]
        return {
            "youtube_indexed": yt_count,
            "tiktok_indexed": tt_count,
            "total_indexed": total
        }

    def get_all_indexed_videos(self) -> List[Dict[str, Any]]:
        """Returns all indexed videos across YouTube and TikTok."""
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM platform_indexed_videos").fetchall()
            return [dict(r) for r in rows]
