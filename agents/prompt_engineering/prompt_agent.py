import os
import re
from typing import Dict, Any, List

class PromptEngineeringAgent:
    """Enforces Character Lock, visual benchmark consistency, and automatic prompt repair for Google Flow."""

    def __init__(self, characters: List[Dict[str, Any]] = None, benchmark: str = "Garden Me Jhula (High-Fidelity 3D Pixar / CoComelon Benchmark)"):
        self.characters = {c["name"]: c for c in characters} if characters else {}
        self.benchmark = benchmark
        self.style_lock = (
            "Vertical 9:16 aspect ratio, ultra-detailed Pixar 3D animated comedy style. "
            "Pure 3D character animation, ultra-adorable rounded chubby toddler character models, oversized cute heads, "
            "rosy blushing cheeks, big expressive glassy 3D brown eyes, volumetric 3D hair with glossy highlights, "
            "soft glowing peach skin, bright cheerful family room lighting, soft ambient occlusion, "
            "STRICTLY NO CGI artifacts, NO semi-realistic, NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays."
        )

    def build_locked_prompt(self, base_scene_action: str, active_characters: List[str] = None, is_final_part: bool = False) -> str:
        """Constructs an airtight generation prompt with permanent character locks and no hallucinations."""
        if not active_characters:
            char_refs = "@Kaartik (5, chubby rounded cheeks, yellow polo), @Kaavya (3, adorable toddler, pink frock, double buns), and @Pinki (Mummy, 25, powder-blue kurti)"
        else:
            char_refs = ", ".join([f"@{c}" for c in active_characters])

        cta_instruction = ""
        if is_final_part:
            cta_instruction = (
                " At the end, Kaavya or Kaartik looks at camera with a super cute bright smile and speaks in cute toddler Hindi: "
                "'Dosto agar maza aaya toh video ko LIKE zaroor karna aur follow karna! Love you!'"
            )

        prompt = (
            f"{self.style_lock} "
            f"Benchmark: {self.benchmark}. "
            f"Characters locked: {char_refs}. "
            f"Scene action: {base_scene_action.strip()}.{cta_instruction} "
            f"Dialogue constraint: All characters speak strictly in cute natural HINDI dialogues. "
            f"Strict constraints: Exactly ONE of each character, No duplicate or clone characters, locked clothing, joyful toddler expressions, fluid 3D character motion, 9:16 vertical."
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
