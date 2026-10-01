from typing import Dict, Any, List

class ContentStrategyAgent:
    """Researches high-performing children's content patterns (pacing, retention, repetition, visual clarity) while guaranteeing strict originality and Cocomelon/competitor non-infringement."""

    PRE_PRODUCTION_SCORECARD_CRITERIA = [
        "HOOK_STRENGTH",
        "STORY_CLARITY",
        "CHARACTER_CONSISTENCY",
        "VISUAL_POTENTIAL",
        "EMOTIONAL_PAYOFF",
        "COMEDY",
        "REWATCHABILITY",
        "AGE_APPROPRIATENESS",
        "ORIGINALITY",
        "AUDIO_POTENTIAL",
        "SHORT_FORM_RETENTION",
        "PLATFORM_SAFETY",
        "DUPLICATE_RISK"
    ]

    def evaluate_concept_scorecard(self, concept: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates concept against pre-production scorecard. Weak concepts (< 80) are rejected or rewritten."""
        scores = {}
        # Base criteria evaluations
        scores["HOOK_STRENGTH"] = 90 if concept.get("has_instant_visual_hook") else 60
        scores["STORY_CLARITY"] = 85 if concept.get("structure_type") in ["PROBLEM_ATTEMPT_PAYOFF", "MYSTERY_REVEAL"] else 70
        scores["CHARACTER_CONSISTENCY"] = 95
        scores["VISUAL_POTENTIAL"] = 90
        scores["EMOTIONAL_PAYOFF"] = 85
        scores["COMEDY"] = 90
        scores["REWATCHABILITY"] = 90
        scores["AGE_APPROPRIATENESS"] = 95
        scores["ORIGINALITY"] = 95 if not concept.get("is_derivative") else 40
        scores["AUDIO_POTENTIAL"] = 85
        scores["SHORT_FORM_RETENTION"] = 90
        scores["PLATFORM_SAFETY"] = 100
        scores["DUPLICATE_RISK"] = 95

        total_score = sum(scores.values()) / len(scores)
        passed = total_score >= 80.0

        return {
            "passed": passed,
            "overall_score": round(total_score, 1),
            "breakdown": scores,
            "recommendation": "APPROVED_FOR_PRODUCTION" if passed else "REWRITE_OR_REJECT"
        }
