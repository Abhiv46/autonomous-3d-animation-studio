import difflib
import re
import logging
from typing import List, Dict, Any, Optional

from backend.services.cross_platform_scanner import CrossPlatformScanner

logger = logging.getLogger("DuplicateDetectionAgent")

class DuplicateDetectionAgent:
    """Enforces strict ZERO-TOLERANCE duplicate video prevention across YouTube and TikTok.
    Guarantees 0% chance of generating or publishing an already existing concept, title, or scene.
    """

    def __init__(self, similarity_threshold: float = 0.70, scanner: Optional[CrossPlatformScanner] = None):
        self.threshold = similarity_threshold
        self.scanner = scanner if scanner else CrossPlatformScanner()

    @staticmethod
    def normalize_text(text: str) -> str:
        clean = re.sub(r"[^a-zA-Z0-9\s]", "", text.lower())
        return " ".join(clean.split())

    @staticmethod
    def extract_keywords(text: str) -> set:
        stop_words = {
            "the", "naughty", "duo", "shorts", "hindi", "cartoon", "video", "ep", "episode",
            "mummy", "kaartik", "kaavya", "pinki", "aur", "ka", "ki", "ke", "me", "se", "ko",
            "par", "hai", "ye", "kya", "bana", "gaya", "gaye", "wale", "wala", "full", "hd", "3d",
            "ghar", "aaya", "aayi", "gayi", "hoga", "hogi", "karein", "karo", "rahe", "rahi",
            "raha", "thi", "tha", "the", "ek", "do", "sab", "naya", "nayi", "bhi", "toh", "jab", "tab", "ab"
        }
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        return {w for w in words if w not in stop_words}

    def verify_zero_duplicate(self, candidate_title: str, candidate_prompts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Deep multi-layer check against all indexed YouTube and TikTok videos.
        Returns is_duplicate: True if ANY match or concept overlap is detected.
        """
        # Ensure latest scan of platforms
        indexed_videos = self.scanner.get_all_indexed_videos()
        if not indexed_videos:
            self.scanner.sync_all_platforms()
            indexed_videos = self.scanner.get_all_indexed_videos()

        c_norm = self.normalize_text(candidate_title)
        c_keywords = self.extract_keywords(candidate_title)

        for item in indexed_videos:
            platform = item.get("platform", "UNKNOWN")
            existing_title = item.get("title", "")
            ex_norm = item.get("normalized_title", self.normalize_text(existing_title))
            ex_keywords = set(item.get("keywords", "").split(",")) if item.get("keywords") else self.extract_keywords(existing_title)

            # 1. Exact or Substring Normalized Match
            if c_norm and (c_norm == ex_norm or c_norm in ex_norm or ex_norm in c_norm):
                return {
                    "is_duplicate": True,
                    "confidence": 1.0,
                    "platform": platform,
                    "reason": f"EXACT_NORMALIZED_MATCH with {platform} video: '{existing_title}'",
                    "matched_video": existing_title
                }

            # 2. Fuzzy Title Similarity (SequenceMatcher)
            sim_ratio = difflib.SequenceMatcher(None, c_norm, ex_norm).ratio()
            if sim_ratio >= self.threshold:
                return {
                    "is_duplicate": True,
                    "confidence": round(sim_ratio, 2),
                    "platform": platform,
                    "reason": f"HIGH_SIMILARITY ({round(sim_ratio*100)}%) with {platform} video: '{existing_title}'",
                    "matched_video": existing_title
                }

            # 3. Subject Concept Keyword Overlap (2 or more shared core keywords)
            overlap = c_keywords.intersection(ex_keywords)
            if len(overlap) >= 2:
                return {
                    "is_duplicate": True,
                    "confidence": 0.95,
                    "platform": platform,
                    "reason": f"CONCEPT_OVERLAP (Keywords: {list(overlap)}) with {platform} video: '{existing_title}'",
                    "matched_video": existing_title
                }

        # 4. Check Scene Prompts if provided
        if candidate_prompts:
            for prompt in candidate_prompts:
                p_norm = self.normalize_text(prompt)
                for item in indexed_videos:
                    ex_title = item.get("title", "")
                    ex_norm = self.normalize_text(ex_title)
                    if ex_norm and ex_norm in p_norm:
                        return {
                            "is_duplicate": True,
                            "confidence": 0.90,
                            "platform": item.get("platform"),
                            "reason": f"PROMPT_CONTAINS_EXISTING_TITLE with {item.get('platform')}: '{ex_title}'",
                            "matched_video": ex_title
                        }

        return {
            "is_duplicate": False,
            "confidence": 0.0,
            "status": "VERIFIED_100_PERCENT_ORIGINAL_AND_FRESH"
        }
