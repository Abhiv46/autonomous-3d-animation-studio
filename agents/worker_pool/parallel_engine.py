import os
import sys
import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.db.database import DatabaseManager
from agents.prompt_engineering.prompt_agent import PromptEngineeringAgent
from agents.quality_control.quality_agent import QualityControlAgent
from agents.seo.seo_agent import YouTubeSEOAgent
from backend.services.assembly_service import VideoAssemblyService
from browser.google_flow.flow_driver import GoogleFlowProjectLockedDriver
from browser.engine.browser_manager import BrowserAutomationEngine

logger = logging.getLogger("ParallelWorkerPool")

class MultiAccountParallelEngine:
    """Manages multi-account parallel video generation across up to 8 Google Flow accounts simultaneously.
    Enforces Strict Project Locking ('The Naughty Duo'), Permanent Character Lock, P0 Incomplete Recovery,
    and automatic credit exhaustion handoff.
    """

    def __init__(self, config: Dict[str, Any], max_concurrent: int = 4, db: Optional[DatabaseManager] = None):
        self.config = config
        self.max_concurrent = min(max_concurrent, len(config.get("google_flow", {}).get("accounts", [])))
        self.db = db if db else DatabaseManager()
        self.accounts = config.get("google_flow", {}).get("accounts", [])
        self.db.sync_accounts(self.accounts)
        
        self.prompt_agent = PromptEngineeringAgent(
            self.config.get("character_lock", {}).get("characters", []),
            benchmark=self.config.get("character_lock", {}).get("quality_benchmark", "Garden Me Jhula (High-Fidelity 3D Pixar)")
        )
        self.qc_agent = QualityControlAgent()
        self.seo_agent = YouTubeSEOAgent()
        self.assembler = VideoAssemblyService()

        self.raw_clips_dir = str(Path(BASE_DIR) / "data" / "raw_clips")
        os.makedirs(self.raw_clips_dir, exist_ok=True)
        self.flow_driver = GoogleFlowProjectLockedDriver(self.raw_clips_dir)

        self._lock = threading.Lock()
        self._running = False

    def claim_next_work_item(self, assigned_slot: int) -> Optional[Dict[str, Any]]:
        """Atomically claims the highest priority incomplete or pending scene across the database."""
        with self._lock:
            with self.db.get_connection() as conn:
                # 1. P0 Check: Find pending part in a PARTIAL / WAITING story first
                part_row = conn.execute("""
                    SELECT p.id, p.story_id, p.part_number, p.scene_label, p.prompt_text, s.title, s.priority
                    FROM story_parts p
                    JOIN stories s ON p.story_id = s.id
                    WHERE p.status = 'PENDING'
                    ORDER BY s.priority ASC, p.part_number ASC
                    LIMIT 1
                """).fetchone()

                if not part_row:
                    return None

                # Mark part as GENERATING immediately to prevent race condition across parallel workers
                conn.execute("""
                    UPDATE story_parts 
                    SET status = 'GENERATING', assigned_account_id = ?
                    WHERE id = ?
                """, (f"acc_{assigned_slot}", part_row["id"]))

                # Mark story state to GENERATING if it was QUEUED
                conn.execute("""
                    UPDATE stories 
                    SET state = CASE WHEN state = 'QUEUED' THEN 'GENERATING' ELSE state END,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (part_row["story_id"],))

                return dict(part_row)

    def execute_worker_task(self, account: Dict[str, Any]) -> Dict[str, Any]:
        """Worker thread lifecycle for a single account slot:
        1. Claims next scene.
        2. Applies Character Lock to prompt.
        3. Executes generation on the designated account slot.
        4. Verifies output and updates DB.
        5. Triggers assembly if entire story is completed.
        """
        slot_idx = account["slot_index"]
        account_email = account["email"]
        logger.info(f"[WORKER /u/{slot_idx}/] Worker started for account: {account_email}")

        item = self.claim_next_work_item(slot_idx)
        if not item:
            logger.info(f"[WORKER /u/{slot_idx}/] No pending scenes in queue. Worker standing by.")
            return {"slot": slot_idx, "status": "IDLE"}

        part_id = item["id"]
        story_id = item["story_id"]
        logger.info(f"[WORKER /u/{slot_idx}/] Processing Scene {item['part_number']} of Story {story_id}: '{item['title'][:35]}...'")

        # Step 1: Format Prompt with Character Lock
        locked_prompt = self.prompt_agent.build_locked_prompt(item["prompt_text"])
        out_filename = f"{part_id}.mp4"
        out_path = os.path.join(self.raw_clips_dir, out_filename)

        # Simulation Mode check (allows zero-risk stress tests & unit tests)
        if os.getenv("SIMULATION", "false").lower() == "true":
            logger.info(f"[SIMULATION /u/{slot_idx}/] Generating mock scene file for {part_id}...")
            time.sleep(2)
            # Create a lightweight dummy file if not exists
            with open(out_path, "wb") as f:
                f.write(b"\x00" * 150000)
            success = True
        else:
            # Step 2: Google Flow Browser Execution with Strict Project Lock
            success = self._run_browser_generation(account, locked_prompt, out_filename)

        if success and os.path.exists(out_path):
            logger.info(f"[WORKER /u/{slot_idx}/] Scene {part_id} generation succeeded -> {out_path}")
            self.db.update_part_status(part_id, "COMPLETED", account_id=f"acc_{slot_idx}", raw_path=out_path)
            self._check_and_trigger_story_assembly(story_id)
            return {"slot": slot_idx, "status": "COMPLETED", "part_id": part_id, "story_id": story_id}
        else:
            logger.warning(f"[WORKER /u/{slot_idx}/] Scene {part_id} failed or credit exhausted. Re-queueing part safely.")
            with self._lock:
                with self.db.get_connection() as conn:
                    conn.execute("UPDATE story_parts SET status = 'PENDING', assigned_account_id = NULL WHERE id = ?", (part_id,))
                    conn.execute("UPDATE stories SET state = 'PARTIAL', priority = 0 WHERE id = ?", (story_id,))
            return {"slot": slot_idx, "status": "FAILED_OR_REQUEUED", "part_id": part_id}

    def _run_browser_generation(self, account: Dict[str, Any], prompt: str, out_filename: str) -> bool:
        """Executes actual Google Flow generation with Playwright persistent context."""
        slot_idx = account["slot_index"]
        project_name = account.get("project_name", "The Naughty Duo")
        project_id = account.get("project_id")

        browser_dir = str(Path(BASE_DIR) / "browser_session")
        if not os.path.exists(browser_dir):
            browser_dir = r"C:\TheNaughtyDuo_Automation\browser_session"

        engine = BrowserAutomationEngine(
            browser_exe=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            user_data_dir=browser_dir,
            headless=True
        )

        try:
            ctx = engine.launch()
            page = ctx.new_page()
            
            # Strict Project Lock Navigation
            self.flow_driver.open_configured_project(page, slot_idx, project_id, project_name)
            
            # Submit Prompt & Download
            self.flow_driver.generate_and_download_scene(page, prompt, out_filename, timeout_seconds=120)
            ctx.close()
            return True
        except Exception as e:
            logger.error(f"[WORKER /u/{slot_idx}/] Browser generation error: {e}")
            engine.close()
            return False

    def _check_and_trigger_story_assembly(self, story_id: str):
        """Checks if all parts of a story are COMPLETED. If so, triggers Assembly, QC, and Publication Queue."""
        with self._lock:
            with self.db.get_connection() as conn:
                parts = conn.execute("SELECT id, status, raw_video_path FROM story_parts WHERE story_id = ? ORDER BY part_number ASC", (story_id,)).fetchall()
                if not parts:
                    return

                all_done = all(p["status"] == "COMPLETED" and p["raw_video_path"] and os.path.exists(p["raw_video_path"]) for p in parts)
                if not all_done:
                    done_count = sum(1 for p in parts if p["status"] == "COMPLETED")
                    conn.execute("UPDATE stories SET state = 'PARTIAL', priority = 0 WHERE id = ?", (story_id,))
                    logger.info(f"[ORCHESTRATOR] Story {story_id} progress: {done_count}/{len(parts)} parts completed. Remaining locked as P0.")
                    return

                # Mark story as COMPLETING
                conn.execute("UPDATE stories SET state = 'COMPLETING' WHERE id = ?", (story_id,))

        # Run Video Assembly
        logger.info(f"[ASSEMBLER] All parts completed for Story {story_id}! Stitching final video...")
        part_paths = [p["raw_video_path"] for p in parts]
        try:
            final_video = self.assembler.merge_story_parts(story_id, part_paths)
            
            # Quality Control
            qc_result = self.qc_agent.run_preflight_check(final_video)
            logger.info(f"[QC_AGENT] Story {story_id} preflight QC passed: {qc_result.get('passed', True)}")

            with self._lock:
                with self.db.get_connection() as conn:
                    conn.execute("UPDATE stories SET state = 'COMPLETED', priority = 5 WHERE id = ?", (story_id,))
                    # Record video output
                    conn.execute("""
                        INSERT OR REPLACE INTO videos (id, story_id, filepath, status)
                        VALUES (?, ?, ?, 'READY_TO_PUBLISH')
                    """, (f"vid_{story_id}", story_id, final_video))

            logger.info(f"[PIPELINE] Story {story_id} FULLY PRODUCED & READY FOR PUBLICATION! -> {final_video}")
        except Exception as e:
            logger.error(f"[ASSEMBLER] Assembly failed for {story_id}: {e}")
            with self._lock:
                with self.db.get_connection() as conn:
                    conn.execute("UPDATE stories SET state = 'RETRY_REQUIRED', priority = 0 WHERE id = ?", (story_id,))

    def run_parallel_batch(self, account_slots: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """Dispatches parallel workers simultaneously across selected or all available account slots."""
        available_accounts = self.accounts
        if account_slots is not None:
            available_accounts = [a for a in self.accounts if a["slot_index"] in account_slots]

        target_pool = available_accounts[:self.max_concurrent]
        logger.info(f"[PARALLEL_POOL] Launching {len(target_pool)} parallel workers across account slots: {[a['slot_index'] for a in target_pool]}")

        results = []
        with ThreadPoolExecutor(max_workers=len(target_pool)) as executor:
            future_to_acc = {executor.submit(self.execute_worker_task, acc): acc for acc in target_pool}
            for future in as_completed(future_to_acc):
                acc = future_to_acc[future]
                try:
                    res = future.result()
                    results.append(res)
                except Exception as exc:
                    logger.error(f"[PARALLEL_POOL] Worker for /u/{acc['slot_index']}/ generated exception: {exc}")
                    results.append({"slot": acc["slot_index"], "status": "ERROR", "error": str(exc)})

        return results
