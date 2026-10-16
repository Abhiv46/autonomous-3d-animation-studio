from __future__ import annotations

from typing import Any, Dict, List


class TrendResearchAgent:
    """Finds the strongest Hook + retention pattern for family Shorts and TikTok storytelling."""

    def __init__(self, trend_seed: Dict[str, Any] | None = None):
        self.trend_seed = trend_seed or {
            "platforms": {
                "youtube": {
                    "hook_window_seconds": 2,
                },
                "tiktok": {
                    "hook_window_seconds": 1,
                },
            }
        }

    def research_trends(self, niche: str = "kids family comedy", platform: str = "youtube", limit: int = 5) -> List[Dict[str, Any]]:
        topic_bank = [
            "tiny problem with funny reaction",
            "sudden surprise reveal",
            "family challenge with cute win",
            "sleepy toddler mischief",
            "sharing moment turned funny",
            "daily routine comedy",
        ]
        platform_cfg = self.trend_seed["platforms"].get(
            platform,
            self.trend_seed["platforms"]["youtube"],
        )
        items: List[Dict[str, Any]] = []
        for index, topic in enumerate(topic_bank[:limit], start=1):
            score = 82 + index * 3
            hook = (
                f"Open on the exact surprise in the first {platform_cfg['hook_window_seconds']} seconds: "
                f"{topic} with a huge reaction, bright colors, and immediate payoff."
            )
            items.append(
                {
                    "topic": topic,
                    "hook": hook,
                    "heuristic_score": min(score, 99),
                    "score_basis": "editorial_heuristic_not_live_trend_or_audience_data",
                    "reason": "Editorial hypothesis: curiosity + emotional payoff + repeatable family pattern",
                }
            )
        return items

    def build_daily_story_matrix(self, platform: str = "youtube", max_topics: int = 5) -> List[Dict[str, Any]]:
        items = self.research_trends(platform=platform, limit=max_topics)
        return [
            {
                "topic": item["topic"],
                "hook": item["hook"],
                "heuristic_score": item["heuristic_score"],
                "score_basis": item["score_basis"],
                "publish_slot": "prime_window",
            }
            for item in items
        ]


class ThumbnailEngineerAgent:
    """Generates thumbnail rules that make the first frame impossible to ignore."""

    def design_thumbnail(self, title: str, concept: str, platform: str = "youtube") -> Dict[str, Any]:
        face_text = title.strip().split()[:3]
        headline = " ".join(face_text) if face_text else "Funny Family Moment"
        return {
            "platform": platform,
            "thumbnail_title": headline[:24],
            "layout": "close-up face + dramatic reaction + one short text line",
            "color_rule": "high contrast, warm yellow + pink + red accents",
            "text_rule": "max 3 words, 3.5x height, huge face expression",
            "cta": "SURPRISE REACTION",
            "concept": concept,
            "safe_guidance": "Keep the character expression clear and 9:16 framing consistent; no text clutter.",
        }


class PerformanceAnalyticsAgent:
    """Scores the content after publishing and suggests the next content move."""

    def evaluate_post(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        required_metrics = (
            "average_watch_time",
            "retention_rate",
            "click_through_rate",
            "likes_ratio",
        )
        missing = [key for key in required_metrics if metrics.get(key) is None]
        if missing:
            return {
                "available": False,
                "score": None,
                "recommendation": "collect_analytics",
                "missing_metrics": missing,
                "insights": ["No performance score was calculated because required live metrics are missing."],
            }

        watch_time = float(metrics["average_watch_time"])
        retention = float(metrics["retention_rate"])
        ctr = float(metrics["click_through_rate"])
        likes = float(metrics["likes_ratio"])
        score = (watch_time * 1.2) + (retention * 0.8) + (ctr * 80) + (likes * 20)
        if score >= 90:
            recommendation = "double_down_same_pattern"
        elif score >= 70:
            recommendation = "keep_formula_and_test_variation"
        elif score >= 50:
            recommendation = "change_hook_faster"
        else:
            recommendation = "rebuild_story_structure"
        return {
            "available": True,
            "score": round(score, 2),
            "recommendation": recommendation,
            "insights": [
                "Hook must land within the first 2 seconds.",
                "Keep the payoff within the first 15 seconds of the short.",
                "Use a visual surprise before the dialogue explanation.",
            ],
        }


class ComplianceGuardAgent:
    """Keeps publishing safe, policy-aware, and platform-compliant."""

    def check_content(self, title: str, concept: str, cta: str, platform: str) -> Dict[str, Any]:
        issues: List[str] = []
        if len(title) > 100:
            issues.append("TITLE_TOO_LONG")
        if "clickbait" in concept.lower() or "misleading" in concept.lower():
            issues.append("MISLEADING_PROMISE")
        if "subscribe" not in cta.lower() and "follow" not in cta.lower():
            issues.append("MISSING_CTA")
        if platform not in {"youtube", "tiktok"}:
            issues.append("UNSUPPORTED_PLATFORM")
        return {
            "safe": not issues,
            "issues": issues,
            "platform": platform,
            "verdict": "PASS" if not issues else "REVIEW_REQUIRED",
        }


class LocalOpsDashboardAgent:
    """Creates a readable per-agent status board for the local ops screen."""

    def build_dashboard(self, batch: List[Dict[str, Any]], quality_results: List[Dict[str, Any]], upload_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        agent_status = [
            {"agent": "ResearchAgent", "status": "active", "job": "trending hook selection"},
            {"agent": "ScriptAgent", "status": "active", "job": "scene rhythm and CTA build"},
            {"agent": "GoogleFlowGenerationAgent", "status": "active", "job": "locked multi-scene prompt packs"},
            {"agent": "EditingAgent", "status": "active", "job": "cut, pace, and sound cleanup"},
            {"agent": "QualityAssuranceAgent", "status": "active", "job": "validate CTA + story lock + safety"},
            {"agent": "SEOAgent", "status": "active", "job": "title, tags, metadata, and slots"},
            {"agent": "ThumbnailEngineerAgent", "status": "active", "job": "thumbnail and first-frame attention"},
            {"agent": "ComplianceGuardAgent", "status": "active", "job": "policy and platform checks"},
        ]
        quality_gate = all(item.get("passed", False) for item in quality_results) if quality_results else False
        live_ready = bool(upload_results) and all(
            item.get("status") == "LIVE_POSTED" for item in upload_results
        )
        return {
            "agent_status": agent_status,
            "batch_count": len(batch),
            "quality_gate": quality_gate,
            "live_upload_ready": live_ready,
            "overall_health": "green" if quality_gate and live_ready else "amber",
            "decision": (
                "Proceed only when quality checks pass and every post is confirmed live."
                if quality_gate and live_ready
                else "Hold publishing: resolve failed QA checks, missing assets, or live-upload blockers."
            ),
        }


__all__ = [
    "TrendResearchAgent",
    "ThumbnailEngineerAgent",
    "PerformanceAnalyticsAgent",
    "ComplianceGuardAgent",
    "LocalOpsDashboardAgent",
]
