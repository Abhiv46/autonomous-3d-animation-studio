import difflib
from typing import List, Dict, Any

class DuplicateDetectionAgent:
    """Calculates semantic and text similarity against historical fingerprint registry to prevent accidental duplicate production."""

    def __init__(self, similarity_threshold: float = 0.82):
        self.threshold = similarity_threshold

    def evaluate_similarity(self, candidate_title: str, candidate_prompts: List[str], historical_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        for entry in historical_entries:
            # Check title similarity
            title_sim = difflib.SequenceMatcher(None, candidate_title.lower(), entry.get("title", "").lower()).ratio()
            if title_sim >= self.threshold:
                return {
                    "is_duplicate": True,
                    "similarity_score": round(title_sim, 2),
                    "reason": f"Title highly similar ({round(title_sim*100)}%) to existing story: '{entry.get('title')}'",
                    "existing_story_id": entry.get("id")
                }

            # Check prompt similarity
            for c_prompt in candidate_prompts:
                for hist_prompt in entry.get("prompts", []):
                    prompt_sim = difflib.SequenceMatcher(None, c_prompt.lower(), hist_prompt.lower()).ratio()
                    if prompt_sim >= self.threshold:
                        return {
                            "is_duplicate": True,
                            "similarity_score": round(prompt_sim, 2),
                            "reason": f"Scene prompt highly similar ({round(prompt_sim*100)}%) to existing story ID: {entry.get('id')}",
                            "existing_story_id": entry.get("id")
                        }

        return {"is_duplicate": False, "similarity_score": 0.0}
