import os
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None):
        if not db_path:
            base_dir = Path(__file__).resolve().parent.parent.parent
            data_dir = base_dir / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(data_dir / "content_engine.db")
            
        self.db_path = db_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        migrations_dir = Path(__file__).resolve().parent.parent.parent / "database" / "migrations"
        if migrations_dir.exists():
            with self.get_connection() as conn:
                for sql_file in sorted(migrations_dir.glob("*.sql")):
                    with open(sql_file, "r", encoding="utf-8") as f:
                        conn.executescript(f.read())

    @staticmethod
    def generate_hash(text: str) -> str:
        return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()

    def sync_accounts(self, accounts: List[Dict[str, Any]]):
        with self.get_connection() as conn:
            for acc in accounts:
                conn.execute("""
                    INSERT INTO accounts (id, slot_index, email, tier, project_id, project_name, status, available_credits)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(slot_index) DO UPDATE SET
                        email=excluded.email,
                        tier=excluded.tier,
                        project_id=excluded.project_id,
                        project_name=excluded.project_name,
                        status=excluded.status,
                        available_credits=excluded.available_credits;
                """, (
                    f"acc_{acc['slot_index']}",
                    acc["slot_index"],
                    acc["email"],
                    acc.get("tier", "FREE"),
                    acc.get("project_id"),
                    acc.get("project_name"),
                    acc.get("status", "ACTIVE"),
                    acc.get("max_daily_credits", 50)
                ))

    def sync_characters(self, characters: List[Dict[str, Any]]):
        with self.get_connection() as conn:
            for ch in characters:
                conn.execute("""
                    INSERT INTO characters (id, name, role, age, appearance_description, locked_clothing, voice_description, is_locked)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                    ON CONFLICT(id) DO UPDATE SET
                        appearance_description=excluded.appearance_description,
                        locked_clothing=excluded.locked_clothing,
                        voice_description=excluded.voice_description;
                """, (
                    ch["id"],
                    ch["name"],
                    ch["role"],
                    ch.get("age", 5),
                    ch["appearance"],
                    ch["locked_clothing"],
                    ch.get("voice_style", "")
                ))

    def check_duplicate_story(self, title: str, prompts: List[str]) -> Dict[str, Any]:
        """Checks if a story title or prompts have already been registered or generated."""
        story_hash = self.generate_hash(title)
        prompt_hashes = [self.generate_hash(p) for p in prompts]

        with self.get_connection() as conn:
            # 1. Check title / story hash
            row = conn.execute("SELECT id, title, state FROM stories WHERE story_hash = ?", (story_hash,)).fetchone()
            if row:
                return {
                    "is_duplicate": True,
                    "reason": "STORY_TITLE_EXACT_MATCH",
                    "existing_story_id": row["id"],
                    "state": row["state"]
                }

            # 2. Check cross-platform YouTube & TikTok live index
            clean_title = "".join(c for c in title.lower() if c.isalnum() or c.isspace()).strip()
            norm_title = " ".join(clean_title.split())
            if norm_title:
                plat_match = conn.execute("""
                    SELECT platform, title FROM platform_indexed_videos
                    WHERE normalized_title = ? OR normalized_title LIKE ? OR ? LIKE ('%' || normalized_title || '%')
                    LIMIT 1
                """, (norm_title, f"%{norm_title}%", norm_title)).fetchone()
                if plat_match:
                    return {
                        "is_duplicate": True,
                        "reason": f"ALREADY_ON_{plat_match['platform']}",
                        "existing_story_id": plat_match["title"],
                        "state": "PUBLISHED"
                    }

            # 3. Check prompt hashes against fingerprints
            for ph in prompt_hashes:
                fp = conn.execute("""
                    SELECT f.story_id, s.title, s.state 
                    FROM content_fingerprints f
                    JOIN stories s ON f.story_id = s.id
                    WHERE f.prompt_hash = ?
                """, (ph,)).fetchone()
                if fp:
                    return {
                        "is_duplicate": True,
                        "reason": "PROMPT_FINGERPRINT_MATCH",
                        "existing_story_id": fp["story_id"],
                        "state": fp["state"]
                    }

        return {"is_duplicate": False}

    def register_story(self, story_id: str, title: str, concept: str, structure: str, parts: List[Dict[str, Any]], priority: int = 2) -> str:
        dup = self.check_duplicate_story(title, [p["prompt_text"] for p in parts])
        if dup["is_duplicate"]:
            raise ValueError(f"Duplicate story rejected: {dup['reason']} (Existing: {dup['existing_story_id']})")

        story_hash = self.generate_hash(title)
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO stories (id, title, concept_summary, structure_type, story_hash, total_parts, state, priority)
                VALUES (?, ?, ?, ?, ?, ?, 'QUEUED', ?)
            """, (story_id, title, concept, structure, story_hash, len(parts), priority))

            for p in parts:
                p_hash = self.generate_hash(p["prompt_text"])
                conn.execute("""
                    INSERT INTO story_parts (id, story_id, part_number, scene_label, prompt_text, prompt_hash, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'PENDING')
                """, (f"{story_id}-P{p['part_number']:02d}", story_id, p["part_number"], p["scene_label"], p["prompt_text"], p_hash))

                conn.execute("""
                    INSERT INTO content_fingerprints (id, story_id, prompt_hash, title_hash)
                    VALUES (?, ?, ?, ?)
                """, (f"fp_{story_id}_{p['part_number']}", story_id, p_hash, story_hash))

        return story_id

    def get_highest_priority_job(self) -> Optional[Dict[str, Any]]:
        """P0 (incomplete story recovery) always takes precedence over new stories."""
        with self.get_connection() as conn:
            # Check for P0 incomplete / partial stories first
            row = conn.execute("""
                SELECT * FROM stories 
                WHERE state IN ('PARTIAL', 'WAITING_FOR_CREDITS', 'RETRY_REQUIRED')
                ORDER BY priority ASC, updated_at ASC LIMIT 1
            """).fetchone()

            if not row:
                # Normal queued stories
                row = conn.execute("""
                    SELECT * FROM stories 
                    WHERE state = 'QUEUED'
                    ORDER BY priority ASC, created_at ASC LIMIT 1
                """).fetchone()

            if not row:
                return None

            story = dict(row)
            parts = conn.execute("SELECT * FROM story_parts WHERE story_id = ? ORDER BY part_number ASC", (story["id"],)).fetchall()
            story["parts"] = [dict(p) for p in parts]
            return story

    def update_part_status(self, part_id: str, status: str, account_id: Optional[str] = None, raw_path: Optional[str] = None, error_msg: Optional[str] = None):
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE story_parts SET
                    status = ?,
                    assigned_account_id = COALESCE(?, assigned_account_id),
                    raw_video_path = COALESCE(?, raw_video_path),
                    error_message = ?,
                    generated_at = CASE WHEN ? = 'COMPLETED' THEN CURRENT_TIMESTAMP ELSE generated_at END
                WHERE id = ?
            """, (status, account_id, raw_path, error_msg, status, part_id))

            # Update parent story state
            part = conn.execute("SELECT story_id FROM story_parts WHERE id = ?", (part_id,)).fetchone()
            if part:
                s_id = part["story_id"]
                all_parts = conn.execute("SELECT status FROM story_parts WHERE story_id = ?", (s_id,)).fetchall()
                statuses = [p["status"] for p in all_parts]
                
                if all(s == 'COMPLETED' for s in statuses):
                    conn.execute("UPDATE stories SET state = 'COMPLETED', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (s_id,))
                elif any(s == 'COMPLETED' for s in statuses):
                    conn.execute("UPDATE stories SET state = 'PARTIAL', priority = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (s_id,))
                elif any(s == 'FAILED' for s in statuses):
                    conn.execute("UPDATE stories SET state = 'RETRY_REQUIRED', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (s_id,))

    def log_system_error(self, component: str, error_type: str, severity: str, message: str, story_id: Optional[str] = None, account_id: Optional[str] = None, screenshot_path: Optional[str] = None, recovery_attempted: Optional[str] = None, recovery_successful: bool = False):
        err_id = f"err_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO system_errors (id, component, error_type, severity, message, story_id, account_id, screenshot_path, recovery_attempted, recovery_successful)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (err_id, component, error_type, severity, message, story_id, account_id, screenshot_path, recovery_attempted, 1 if recovery_successful else 0))
        return err_id
