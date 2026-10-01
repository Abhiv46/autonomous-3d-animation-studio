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
            "category_id": "1", # Film & Animation
            "made_for_kids": True
        }
