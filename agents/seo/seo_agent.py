from typing import Dict, Any, List


class YouTubeSEOAgent:
    """Generates natural, click-worthy, child-safe metadata without keyword stuffing or deceptive tactics."""

    def generate_metadata(self, story_title: str, concept: str, characters: List[str]) -> Dict[str, Any]:
        clean_title = f"{story_title.strip()} #TheNaughtyDuo #shorts"[:95]

        description = (
            f"Kaartik aur Kaavya ki nayi mazedaar 3D animated comedy story! 🌟\n\n"
            f"{concept.strip()}\n\n"
            f"❤️ Video thodi si bhi achi lagi ho toh LIKE zaroor karein aur roz nayi funny family stories ke liye "
            f"@TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔✨\n"
            f"Comment me batayein agla prank kaunsa dekhna chahte hain! 👇\n\n"
            f"#TheNaughtyDuo #shorts #viral #3danimation #comedy #cartoonhindi #familycomedy #moralstories"
        )

        tags = [
            "The Naughty Duo", "TheNaughtyDuo", "Kaartik and Kaavya",
            "Hindi Cartoons", "3D Animation", "Kids Comedy",
            "Moral Stories", "Pixar Style", "Family Entertainment", "Shorts"
        ]

        return {
            "title": clean_title,
            "description": description,
            "tags": tags,
            "category_id": "1",  # Film & Animation
            "made_for_kids": True
        }


class ViralSchedulingAgent:
    """Chooses best publish timing for each platform using the configured prime slots."""

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}

    def choose_best_slot(self, platform: str, preferred_day: str | None = None) -> Dict[str, Any]:
        platform_cfg = self.config.get("platforms", {}).get(platform, {})
        slots = platform_cfg.get("prime_slots_ist", ["13:00", "17:30", "20:30"])
        day = preferred_day or "daily"
        selected_slot = slots[0] if slots else "13:00"
        return {
            "platform": platform,
            "day": day,
            "slot_ist": selected_slot,
            "reason": "Prime audience window for high retention and stronger Shorts CTR",
        }

    def build_seo_pack(self, title: str, concept: str, platform: str) -> Dict[str, Any]:
        seo = YouTubeSEOAgent().generate_metadata(title, concept, ["Kaavya", "Kaartik", "Pinki"])
        seo["publish_window"] = self.choose_best_slot(platform)
        seo["pinned_comment"] = (
            f"Aapko konsa next prank aur story dekhna chahiye? Comment karo aur The Naughty Duo ko subscribe karo 🔔"
        )
        seo["hashtags"] = ["#TheNaughtyDuo", "#shorts", "#hindiCartoon", "#kidscomedy", "#familyfun"]
        return seo
