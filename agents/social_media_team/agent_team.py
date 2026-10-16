from __future__ import annotations

import json
import os
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents.google_flow.google_flow_agent import GoogleFlowGenerationAgent
from agents.prompt_engineering.prompt_agent import PromptEngineeringAgent
from agents.quality_control.quality_agent import QualityAssuranceAgent
from agents.seo.seo_agent import ViralSchedulingAgent
from agents.viral_growth.growth_agent import (
    ComplianceGuardAgent,
    LocalOpsDashboardAgent,
    PerformanceAnalyticsAgent,
    ThumbnailEngineerAgent,
    TrendResearchAgent,
)
from platforms.live_production import LiveProductionGate
from platforms.youtube.youtube_adapter import YouTubePlatformAdapter
from platforms.tiktok.tiktok_adapter import TikTokPlatformAdapter


@dataclass
class AgentTask:
    platform: str
    idea: Dict[str, Any]
    account: Dict[str, Any]
    script: Dict[str, Any]
    edit_plan: Dict[str, Any]
    publishing_payload: Dict[str, Any]


class ResearchAgent:
    """Generates a curated shortlist of high-retention content ideas for kids' family content."""

    DEFAULT_TOPICS = [
        "daily family routine comedy",
        "tiny toddler problem and playful payoff",
        "imaginative indoor adventure",
        "cute learning moment with siblings",
        "unexpected surprise reveal",
        "gentle bedtime routine with humor",
        "tiny competition with funny ending",
        "simple kindness or sharing lesson",
    ]

    def generate_ideas(self, niche: str = "family kids fun", limit: int = 5) -> List[Dict[str, Any]]:
        ideas: List[Dict[str, Any]] = []
        for idx, topic in enumerate(self.DEFAULT_TOPICS[:limit], start=1):
            title = f"{topic.title()} {idx}"
            hook = self._build_hook(topic)
            ideas.append(
                {
                    "id": f"idea-{idx:02d}",
                    "niche": niche,
                    "topic": topic,
                    "title": title,
                    "hook": hook,
                    "target_platform": "youtube",
                    "estimated_retention": 68 + (idx * 3),
                }
            )
        return ideas

    def _build_hook(self, topic: str) -> str:
        return f"Start with a fast visual surprise in the first 2 seconds: {topic} with an adorable reaction, bright color palette, and a punchy family payoff."


class ScriptAgent:
    """Turns a content idea into a short-form script with hook, beats, and ending CTA."""

    def write_script(self, idea: Dict[str, Any], platform: str) -> Dict[str, Any]:
        platform_duration = 45 if platform == "youtube" else 60
        script = {
            "title": idea["title"],
            "platform": platform,
            "duration_seconds": platform_duration,
            "hook": f"{idea['hook']} Quick, playful and visually obvious in the first 1.5 seconds.",
            "beats": [
                "0-5s: Immediate surprise and funny visual",
                "5-20s: Small problem introduced with energetic family reaction",
                "20-38s: Comic escalation or silly effort to solve it",
                "38-52s: Sweet payoff with smile, laughter, and simple lesson",
                "52-60s: Bright camera look and friendly CTA",
            ],
            "cta": "Follow for more cheerful family stories and cute everyday adventures!",
            "language": "Hindi + light bilingual family tone",
        }
        return script


class EditingAgent:
    """Builds a professional edit plan with cuts, cleanup, and pacing cues."""

    def build_edit_plan(self, script: Dict[str, Any], platform: str) -> Dict[str, Any]:
        return {
            "platform": platform,
            "trim_segments": [
                {"start": 0, "end": 4, "action": "keep strongest hook"},
                {"start": 4, "end": 18, "action": "remove dead air and repeated frames"},
                {"start": 18, "end": 36, "action": "keep funny action beats"},
                {"start": 36, "end": 52, "action": "tighten payoff"},
                {"start": 52, "end": script["duration_seconds"], "action": "add closing smile and CTA"},
            ],
            "audio": {
                "mix": "clean dialogue, light music bed, no harsh spikes",
                "subtitle_style": "bold white caps with soft shadow",
            },
            "quality_checks": [
                "No duplicate scenes",
                "No blurry frames",
                "Audio level consistent",
                "Platform-safe content only",
            ],
        }


class PublishingAgent:
    """Builds safe publication metadata and validates platform-specific rules."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.youtube_channel_id = self.config.get("platforms", {}).get("youtube", {}).get("channel_id", "")
        self.tiktok_min_duration = self.config.get("platforms", {}).get("tiktok", {}).get("min_duration_seconds", 60)

    def build_publication_payload(self, idea: Dict[str, Any], script: Dict[str, Any], account: Dict[str, Any], platform: str) -> Dict[str, Any]:
        title = script["title"]
        payload = {
            "platform": platform,
            "account_email": account.get("email"),
            "channel_id": self.youtube_channel_id if platform == "youtube" else "TIKTOK_STUDIO",
            "video_path": f"./data/output/{idea['id']}_{platform}.mp4",
            "title": title,
            "description": f"{idea['hook']}\n\nFollow for more cheerful family stories, daily fun, and adorable toddler moments.",
            "duration_seconds": script["duration_seconds"],
            "tags": ["family fun", "kids content", "cute videos", "daily routine", "hindi family"],
        }
        return payload

    def validate_publication_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        platform = payload.get("platform")
        if platform == "youtube":
            if not payload.get("channel_id"):
                return {"valid": False, "error": "SECURITY_ALERT: Missing channel ID"}
            if payload.get("channel_id") != self.youtube_channel_id:
                return {"valid": False, "error": "SECURITY_ALERT: Channel ID mismatch"}
        if platform == "tiktok":
            duration = float(payload.get("duration_seconds", 0) or 0)
            if duration < self.tiktok_min_duration:
                return {"valid": False, "error": "TIKTOK_POLICY: Duration under 60s minimum"}
        if not payload.get("video_path"):
            return {"valid": False, "error": "MISSING_VIDEO_FILE: No source video selected"}
        return {"valid": True, "error": None}


class AnalyticsAgent:
    """Scores performance and decides next content focus using retention-style metrics."""

    def score_video(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        required_metrics = ("average_watch_time", "retention_rate", "click_through_rate")
        missing = [key for key in required_metrics if metrics.get(key) is None]
        if missing:
            return {
                "available": False,
                "score": None,
                "recommendation": "collect_analytics",
                "missing_metrics": missing,
            }
        watch_time = float(metrics.get("average_watch_time", 0))
        retention = float(metrics.get("retention_rate", 0))
        ctr = float(metrics.get("click_through_rate", 0))
        composite = (watch_time * 0.55) + (retention * 0.35) + (ctr * 2.5)
        return {
            "score": round(composite, 2),
            "recommendation": "double_down" if composite > 65 else "test_new_hook" if composite > 45 else "rework",
        }


class SocialMediaAgentTeam:
    """Coordinates a daily workflow for research, scripting, editing, publishing, and analytics."""

    def __init__(self, config_path: Optional[str | Path] = None):
        base_dir = Path(__file__).resolve().parents[2]
        config_path = Path(config_path) if config_path else base_dir / "config" / "config.json"
        with open(config_path, "r", encoding="utf-8") as handle:
            self.config = json.load(handle)

        self.research_agent = ResearchAgent()
        self.script_agent = ScriptAgent()
        self.editor_agent = EditingAgent()
        self.publisher_agent = PublishingAgent(self.config)
        self.analytics_agent = AnalyticsAgent()
        self.flow_agent = GoogleFlowGenerationAgent()
        self.quality_agent = QualityAssuranceAgent()
        self.scheduler_agent = ViralSchedulingAgent(self.config)
        self.trend_agent = TrendResearchAgent()
        self.thumbnail_agent = ThumbnailEngineerAgent()
        self.performance_agent = PerformanceAnalyticsAgent()
        self.compliance_agent = ComplianceGuardAgent()
        self.dashboard_agent = LocalOpsDashboardAgent()
        self.live_gate = LiveProductionGate(config=self.config, repo_root=str(base_dir))
        self.prompt_agent = PromptEngineeringAgent(
            characters=self.config.get("character_lock", {}).get("characters", []),
            benchmark=self.config.get("character_lock", {}).get("quality_benchmark", "Garden Me Jhula"),
        )
        self.accounts = self.config.get("google_flow", {}).get("accounts", [])

        self.youtube_adapter = YouTubePlatformAdapter(
            token_pickle_path=str(base_dir / "config" / "token.pickle"),
            target_channel_id=self.config.get("platforms", {}).get("youtube", {}).get("channel_id", ""),
        )
        self.tiktok_adapter = TikTokPlatformAdapter(
            target_account_handle=self.config.get("platforms", {}).get("tiktok", {}).get("channel_handle", "@TheNaughtyDuoOfficial")
        )

    def choose_account(self, platform: str, used_slots: Optional[set[int]] = None) -> Dict[str, Any]:
        used_slots = used_slots or set()
        candidates = [
            account for account in self.accounts if account.get("status") == "ACTIVE" and account.get("slot_index") not in used_slots
        ]
        if not candidates:
            raise ValueError(f"No active {platform} account available for this cycle")
        return sorted(candidates, key=lambda item: item.get("slot_index"))[0]

    def prepare_google_flow_story(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        flow_pack = self.flow_agent.build_default_waterpark_story()
        flow_pack["concept_id"] = idea["id"]
        flow_pack["concept_title"] = idea["title"]
        flow_pack["platform_focus"] = "youtube_shorts"
        return flow_pack

    def plan_daily_batch(self, max_videos: int = 3, platform_order: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        platform_order = platform_order or ["youtube", "tiktok", "youtube"]
        ideas = self.research_agent.generate_ideas(limit=max_videos)
        trend_matrix = self.trend_agent.build_daily_story_matrix(platform=platform_order[0], max_topics=max_videos)
        batch: List[Dict[str, Any]] = []
        used_slots: set[int] = set()

        for index, idea in enumerate(ideas[:max_videos]):
            platform = platform_order[index % len(platform_order)]
            account = self.choose_account(platform=platform, used_slots=used_slots)
            used_slots.add(int(account.get("slot_index", 0)))

            flow_story = self.prepare_google_flow_story(idea)
            prompt = self.prompt_agent.build_locked_prompt(
                base_scene_action=f"Story beat for {idea['title']}: {idea['hook']}",
                active_characters=["Kaartik", "Kaavya", "Pinki"],
                is_final_part=(index == max_videos - 1),
            )

            script = self.script_agent.write_script(idea, platform)
            edit_plan = self.editor_agent.build_edit_plan(script, platform)
            thumbnail_plan = self.thumbnail_agent.design_thumbnail(idea["title"], idea["hook"], platform)
            compliance = self.compliance_agent.check_content(idea["title"], idea["hook"], script["cta"], platform)
            publishing_payload = self.publisher_agent.build_publication_payload(idea, script, account, platform)
            validation = self.publisher_agent.validate_publication_payload(publishing_payload)
            if not validation["valid"]:
                raise ValueError(f"Publication validation failed for {idea['title']}: {validation['error']}")

            batch.append(
                {
                    "id": idea["id"],
                    "title": idea["title"],
                    "platform": platform,
                    "account": account,
                    "prompt": prompt,
                    "flow_story": flow_story,
                    "script": script,
                    "edit_plan": edit_plan,
                    "thumbnail_plan": thumbnail_plan,
                    "trend_signal": trend_matrix[index % len(trend_matrix)] if trend_matrix else {"score": 85, "topic": idea["topic"]},
                    "compliance": compliance,
                    "publishing_payload": publishing_payload,
                    "scheduled_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        return batch

    def publish_batch(
        self,
        batch: List[Dict[str, Any]],
        live_mode: bool = False,
        dry_run: bool = True,
        quality_results: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        upload_results: List[Dict[str, Any]] = []
        quality_by_id = {result.get("id"): result for result in (quality_results or [])}
        for item in batch:
            payload = item["publishing_payload"]
            platform = payload["platform"]
            file_path = payload["video_path"]
            quality = quality_by_id.get(item["id"])
            if quality is not None and not quality.get("passed", False):
                upload_results.append({
                    "id": item["id"],
                    "platform": platform,
                    "status": "BLOCKED_QA",
                    "title": item["title"],
                    "account_email": item["account"].get("email"),
                    "payload": payload,
                })
                continue
            force_dry_run = dry_run or not live_mode
            if force_dry_run:
                upload_results.append({
                    "id": item["id"],
                    "platform": platform,
                    "status": "DRY_RUN_ONLY",
                    "title": item["title"],
                    "account_email": item["account"].get("email"),
                    "payload": payload,
                })
                continue
            if not os.path.exists(file_path):
                upload_results.append({
                    "id": item["id"],
                    "platform": platform,
                    "status": "BLOCKED_MISSING_VIDEO",
                    "title": item["title"],
                    "account_email": item["account"].get("email"),
                    "payload": payload,
                })
                continue

            adapter = self.youtube_adapter if platform == "youtube" else self.tiktok_adapter
            upload_response = adapter.upload_short(file_path, {"title": payload["title"], "description": payload["description"], "tags": payload["tags"]})
            upload_results.append({
                "id": item["id"],
                "platform": platform,
                "status": "LIVE_POSTED" if upload_response.get("success") else "FAILED",
                "title": item["title"],
                "account_email": item["account"].get("email"),
                "payload": payload,
                "response": upload_response,
            })
        return upload_results

    def run_daily_cycle(self, max_videos: int = 3, live_mode: bool = False, dry_run: bool = True) -> Dict[str, Any]:
        if live_mode and not dry_run:
            readiness = self.live_gate.inspect()
            if not readiness["ready"]:
                raise PermissionError(
                    "Live publishing is blocked: " + "; ".join(readiness["reasons"])
                )
        batch = self.plan_daily_batch(max_videos=max_videos)
        q_results = self.quality_agent.evaluate_batch(batch)
        upload_results = self.publish_batch(
            batch,
            live_mode=live_mode,
            dry_run=dry_run,
            quality_results=q_results,
        )
        dashboard = self.dashboard_agent.build_dashboard(batch, q_results, upload_results)
        live_gate_status = self.live_gate.inspect()
        items = []
        for item in batch:
            quality_gate = next((result["quality_gate"] for result in q_results if result["id"] == item["id"]), "UNKNOWN")
            upload_status = next((result["status"] for result in upload_results if result["id"] == item["id"]), "PENDING")
            quality_passed = next(
                (result["passed"] for result in q_results if result["id"] == item["id"]),
                False,
            )
            queue_state = "planned"
            if os.path.exists(item["publishing_payload"]["video_path"]):
                queue_state = "generated"
            if quality_passed:
                queue_state = "qc_passed"
            if upload_status == "LIVE_POSTED":
                queue_state = "published"
            elif upload_status in {"BLOCKED_QA", "BLOCKED_MISSING_VIDEO", "FAILED"}:
                queue_state = "blocked"
            items.append(
                {
                    "id": item["id"],
                    "title": item["title"],
                    "platform": item["platform"],
                    "account_email": item["account"].get("email"),
                    "slot_index": item["account"].get("slot_index"),
                    "duration_seconds": item["script"]["duration_seconds"],
                    "hook": item["script"]["hook"],
                    "thumbnail_plan": item["thumbnail_plan"],
                    "trend_signal": item["trend_signal"],
                    "upload_status": upload_status,
                    "quality_gate": quality_gate,
                    "job_state": queue_state,
                    "scheduled_at": item.get("scheduled_at"),
                }
            )
        summary = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "batch_size": len(batch),
            "live_mode": live_mode,
            "dry_run": dry_run,
            "platform_mix": {platform: sum(1 for item in batch if item["platform"] == platform) for platform in ["youtube", "tiktok"]},
            "quality_checks": q_results,
            "publish_slots": {item["platform"]: self.scheduler_agent.choose_best_slot(item["platform"]) for item in batch},
            "live_production_gate": live_gate_status,
            "agent_dashboard": dashboard,
            "trend_research": self.trend_agent.build_daily_story_matrix(platform="youtube", max_topics=max_videos),
            "items": items,
            "job_flow": [
                "planned",
                "generated",
                "qc_passed",
                "scheduled",
                "published",
            ],
        }
        return summary


__all__ = [
    "AgentTask",
    "ResearchAgent",
    "ScriptAgent",
    "EditingAgent",
    "PublishingAgent",
    "AnalyticsAgent",
    "SocialMediaAgentTeam",
]
