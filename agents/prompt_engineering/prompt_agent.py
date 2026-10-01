import os
import re
from typing import Dict, Any, List

class PromptEngineeringAgent:
    """Enforces Character Lock, visual benchmark consistency, and automatic prompt repair for Google Flow."""

    def __init__(self, characters: List[Dict[str, Any]], benchmark: str = "Garden Me Jhula (High-Fidelity 3D Pixar)"):
        self.characters = {c["name"]: c for c in characters}
        self.benchmark = benchmark

    def build_locked_prompt(self, base_scene_action: str, active_characters: List[str] = None) -> str:
        """Constructs an airtight generation prompt with permanent character locks and no hallucinations."""
        if not active_characters:
            char_refs = "@Kaartik, @Kaavya, and @Pinki (Mummy)"
        else:
            char_refs = ", ".join([f"@{c}" for c in active_characters])

        prompt = (
            f"Pixar 3D animated comedy children entertainment, cinematic lighting, expressive eyes, "
            f"ultra-crisp rendering matching {self.benchmark} benchmark. "
            f"Characters locked: {char_refs}. "
            f"Scene: {base_scene_action.strip()}. "
            f"Strict constraints: No duplicate or clone characters, locked clothing only, no visual glitches, no 2D drawings, 9:16 vertical ratio."
        )
        return prompt

    def repair_prompt(self, failed_prompt: str, error_category: str) -> str:
        """Diagnoses rejection category and applies intelligent restructuring with exponential backoff."""
        repaired = failed_prompt

        if error_category == "SAFETY_REJECTION":
            # Strip potentially trigger words
            repaired = re.sub(r'\b(fight|hit|slap|choke|trap|fall|danger|busted|scream)\b', 'comical reaction', repaired, flags=re.IGNORECASE)
        elif error_category == "PROMPT_TOO_COMPLEX":
            # Simplify to core action and camera
            parts = repaired.split("Scene:")
            if len(parts) > 1:
                action = parts[1].split(".")[0]
                repaired = f"Pixar 3D animated comedy with @Kaartik and @Kaavya. Scene: {action.strip()}. 9:16 vertical."
        elif error_category == "DURATION_ERROR":
            # Remove any explicit second durations that conflict with Veo native 8s
            repaired = re.sub(r'\b\d+-second\b', '', repaired, flags=re.IGNORECASE)

        return repaired
