import os
import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

from backend.db.database import DatabaseManager
from agents.content_strategy.strategy_agent import ContentStrategyAgent
from agents.duplicate_detection.duplicate_agent import DuplicateDetectionAgent
from agents.prompt_engineering.prompt_agent import PromptEngineeringAgent
from agents.account_manager.account_agent import AccountManagerAgent
from agents.quality_control.quality_agent import QualityControlAgent
from agents.seo.seo_agent import YouTubeSEOAgent
from platforms.youtube.youtube_adapter import YouTubePlatformAdapter
from platforms.tiktok.tiktok_adapter import TikTokPlatformAdapter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
logger = logging.getLogger("AutonomousOrchestrator")

class AutonomousContentOrchestrator:
    """Master orchestrator coordinating all specialized agents. Enforces P0 incomplete story recovery before starting any new story."""

    def __init__(self, config_path: Optional[str] = None):
        base_dir = Path(__file__).resolve().parent.parent.parent
        if not config_path:
            config_path = base_dir / "config" / "master_config.example.json"

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        db_path = str(base_dir / "data" / "content_engine.db")
        self.db = DatabaseManager(db_path=db_path)

        # Sync master config data to SQLite
        self.db.sync_accounts(self.config.get("google_flow", {}).get("accounts", []))
        self.db.sync_characters(self.config.get("character_lock", {}).get("characters", []))

        # Initialize agents
        self.content_agent = ContentStrategyAgent()
        self.duplicate_agent = DuplicateDetectionAgent()
        self.prompt_agent = PromptEngineeringAgent(
            self.config.get("character_lock", {}).get("characters", []),
            benchmark=self.config.get("character_lock", {}).get("quality_benchmark", "Garden Me Jhula (High-Fidelity 3D Pixar)")
        )
        self.account_agent = AccountManagerAgent(self.config.get("google_flow", {}).get("accounts", []))
        self.qc_agent = QualityControlAgent()
        self.seo_agent = YouTubeSEOAgent()

        # Platforms
        yt_cfg = self.config.get("platforms", {}).get("youtube", {})
        token_path = str(base_dir / "config" / "token.pickle")
        self.yt_adapter = YouTubePlatformAdapter(token_path, yt_cfg.get("channel_id", ""))
        self.tiktok_adapter = TikTokPlatformAdapter()

    def run_next_operational_cycle(self) -> Dict[str, Any]:
        """Core self-healing execution cycle:
        1. Checks database for P0 incomplete jobs (Story recovery).
        2. If incomplete story found, completes missing parts before touching anything new.
        3. If no incomplete story, checks queued stories.
        """
        logger.info("[ORCHESTRATOR] Starting operational cycle. Checking content registry...")
        
        # 1. Fetch highest priority job (P0 incomplete always wins)
        job = self.db.get_highest_priority_job()
        if not job:
            logger.info("[ORCHESTRATOR] Queue is idle. No pending or incomplete jobs found.")
            return {"status": "IDLE", "message": "No jobs in queue"}

        story_id = job["id"]
        logger.info(f"[ORCHESTRATOR] Processing Job: {story_id} (Title: '{job['title']}', State: {job['state']}, Priority: P{job['priority']})")

        # 2. Iterate through parts and identify incomplete scenes
        missing_parts = [p for p in job["parts"] if p["status"] != "COMPLETED"]
        completed_parts = [p for p in job["parts"] if p["status"] == "COMPLETED"]

        logger.info(f"[ORCHESTRATOR] Story {story_id}: {len(completed_parts)} parts completed, {len(missing_parts)} parts pending.")

        if not missing_parts:
            logger.info(f"[ORCHESTRATOR] All parts completed for {story_id}. Progressing to QUALITY_CHECK...")
            return {"status": "READY_FOR_ASSEMBLY", "story_id": story_id}

        # 3. Process the next missing part
        target_part = missing_parts[0]
        part_id = target_part["id"]
        logger.info(f"[ORCHESTRATOR] Resuming generation for {part_id}: '{target_part['scene_label']}'...")

        # 4. Account selection (preserves account continuity or switches on credit exhaustion)
        selected_acc = self.account_agent.select_best_account(required_credits=15, current_slot=target_part.get("assigned_account_id"))
        if not selected_acc:
            logger.warning(f"[ORCHESTRATOR] No accounts with available credits found! Marking Story {story_id} as WAITING_FOR_CREDITS (P0).")
            with self.db.get_connection() as conn:
                conn.execute("UPDATE stories SET state = 'WAITING_FOR_CREDITS', priority = 0 WHERE id = ?", (story_id,))
            return {"status": "HALTED_CREDITS_EXHAUSTED", "story_id": story_id}

        slot_idx = selected_acc["slot_index"]
        logger.info(f"[ORCHESTRATOR] Assigned Account: /u/{slot_idx}/ ({selected_acc['email']}) for Part {part_id}")

        # Check simulation mode
        if os.getenv("SIMULATION", "false").lower() == "true":
            logger.info(f"[SIMULATION] Simulating render and download for {part_id}...")
            simulated_path = f"./data/raw_clips/{part_id}_simulated.mp4"
            self.db.update_part_status(part_id, "COMPLETED", account_id=f"acc_{slot_idx}", raw_path=simulated_path)
            return {"status": "PART_GENERATED_SIMULATED", "part_id": part_id, "story_id": story_id}

        return {"status": "DISPATCHED_TO_WORKER", "part_id": part_id, "account": selected_acc}
