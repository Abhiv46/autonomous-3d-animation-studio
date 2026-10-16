from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, Dict, List, Optional


class GoogleFlowGenerationAgent:
    """Creates locked, production-grade prompt packs for Google Flow generation.

    This agent is designed to enforce stable character identity, consistent layout,
    dangerous prompt avoidance, and exact ordering for multi-scene short-form videos.
    """

    LOCKED_CHARACTERS = {
        "Kaavya": {
            "role": "3.5-year-old daughter",
            "face": "huge dark-brown eyes, chubby cheeks, adorable smile",
            "hair": "double space buns with pastel pink bows",
            "outfit": "pastel striped pajama set in pink, blue, lavender, barefoot",
            "swim_ring": "small pink swim ring",
            "position": "left side of frame",
            "personality": "sassy, clever, playful",
        },
        "Kaartik": {
            "role": "2-year-old son",
            "face": "big brown eyes, chubby cheeks, cute smile",
            "hair": "soft brown tousled hair",
            "outfit": "blue-and-white striped T-shirt, rolled denim shorts, barefoot",
            "swim_ring": "small yellow duck swim ring",
            "prop": "brown teddy bear with red bow tie",
            "position": "right side of frame",
            "personality": "mischievous, curious, tiny hero",
        },
        "Pinki": {
            "role": "mid-20s mother",
            "face": "big brown eyes, bright warm expression",
            "hair": "long dark wavy hair open",
            "outfit": "deep maroon embroidered lehenga, sheer dupatta, gold layered necklace, gold bangles, gold jhumkas",
            "position": "center back when all three are together",
            "personality": "dramatic, funny, loving mother",
        },
    }

    LOCATION_LOCK = {
        "room": "cozy Indian living room turned into a playful home water park",
        "window": "large window on the left with warm daylight",
        "sofa": "cream sofa in center used as a slide",
        "decor": "marigold garland and brass diya on the right",
        "tub": "big shallow water tub on rug in front of the slide",
        "layout": "same layout in every scene, no room changes from scene to scene",
    }

    BASE_STYLE = (
        "Premium 3D animated Pixar-like cinematic look, warm sunlight, colorful family comedy, "
        "soft depth, smooth cinematic motion, high retention, charming toddler energy, "
        "family-safe, highly engaging, kid-friendly, clean and polished visuals."
    )

    NEGATIVE_PROMPTS = [
        "no extra characters",
        "no random family members",
        "no body part distortion",
        "no warped hands or fingers",
        "no extra limbs",
        "no scary tone",
        "no dark lighting",
        "no deep water",
        "no danger",
        "no crying",
        "no adult body proportions on children",
        "no extra outfits or costume changes",
        "no text in the frame except final LIKE, SUBSCRIBE, and THE NAUGHTY DUO in scene 8",
        "no watermarks",
        "no logo clutter",
        "no mirrored room layout",
        "no change in hairstyles, faces, outfits, or jewelry",
    ]

    def build_negative_prompt(self) -> str:
        return ", ".join(self.NEGATIVE_PROMPTS)

    def build_character_lock_block(self) -> str:
        lock_lines = []
        for name, data in self.LOCKED_CHARACTERS.items():
            lock_lines.append(
                f"{name}: {data['role']}, {data['face']}, hair: {data['hair']}, outfit: {data['outfit']}, "
                f"position: {data['position']}, personality: {data['personality']}"
            )
        return " ".join(lock_lines)

    def build_scene_prompt(self, scene_number: int, scene_title: str, scene_description: str, dialogue: Optional[str] = None) -> str:
        scene_prompts = {
            1: "Start mid-action. Pinki opens the door and freezes in comic shock. The room is transformed into a home water park with cushion slide, shallow water tub, soap bubbles, and a playful splash vibe. Kaavya sits on the left in a pink ring with a proud smile. Kaartik sits on the right with a duck ring and teddy bear. Pinki stares in disbelief.",
            2: "Kaavya and Kaartik are happily preparing the water park. Kaavya is confident and bossy, Kaartik pours water into the tub while holding teddy. Keep the room warm and lively. The playful setup should feel handcrafted and funny.",
            3: "Kaavya acts like a tiny engineer and directs the setup. Kaartik carries a bucket with teddy tucked under his arm. They cover the sofa cushion with a blue plastic sheet and arrange the play zone. Bubbles fill the room.",
            4: "Kaartik slides down the sofa cushion in slow motion and lands in the shallow water with a joyful splash. Water droplets sparkle in sunlight. Kaavya cheers and runs forward with excitement.",
            5: "Pinki rushes in to stop them, steps on foam, slips in comic slow motion, and slides into the tub with a funny splash. Kaavya and Kaartik laugh hysterically. No harm, only comedy.",
            6: "Pinki is now in the tub laughing and splashing the kids. Kaavya and Kaartik splash back. Teddy floats on the duck. Warm family chaos with joyful faces and playful energy.",
            7: "Wide shot. The entire room is full of water, bubbles, and family laughter. Pinki stands with wet dupatta, hands on hips, looking dramatic. Kaavya points at Kaartik, Kaartik points at teddy. Freeze-frame comedy moment.",
            8: "Front-facing eye-level shot. Kaavya points to a glowing blue thumbs-up icon and gives a cute thumbs-up. Kaartik hugs teddy and presses a bright red SUBSCRIBE button with his tiny hand. Pinki smiles warmly and waves. Big banner says THE NAUGHTY DUO. End with clean, premium, cheerful CTA.",
        }

        if scene_number in scene_prompts:
            description = scene_prompts[scene_number]
        else:
            description = scene_description

        if dialogue:
            description = f"{description} Dialogue: {dialogue}"

        return (
            f"{self.BASE_STYLE} "
            f"{self.LOCATION_LOCK['room']}. {self.LOCATION_LOCK['window']}. {self.LOCATION_LOCK['sofa']}. "
            f"{self.LOCATION_LOCK['decor']}. {self.LOCATION_LOCK['tub']}. "
            f"Characters: {self.build_character_lock_block()}. "
            f"Scene {scene_number}: {scene_title}. "
            f"Story beat: {description}. "
            f"Aspect ratio 9:16 vertical. Resolution 360x640 preferred. Duration 8 seconds. "
            f"Keep the exact character placement: Kaavya left, Kaartik right, Pinki center/back when together. "
            f"Scene continuity must be exact and polished."
        )

    def build_story_prompt_pack(self, title: str, hook: str, scenes: List[Dict[str, Any]], extra_notes: Optional[str] = None) -> Dict[str, Any]:
        packed_scenes: List[Dict[str, Any]] = []
        for item in scenes:
            scene_num = int(item.get("scene_number", 1))
            scene_title = item.get("title", f"Scene {scene_num}")
            scene_description = item.get("description", "")
            dialogue = item.get("dialogue")
            packed_scenes.append(
                {
                    "scene_number": scene_num,
                    "title": scene_title,
                    "prompt": self.build_scene_prompt(scene_num, scene_title, scene_description, dialogue),
                    "duration_seconds": item.get("duration_seconds", 8),
                    "dialogue": dialogue,
                }
            )

        return {
            "title": title,
            "hook": hook,
            "aspect_ratio": "9:16",
            "resolution": "360x640",
            "duration_seconds": sum(scene["duration_seconds"] for scene in packed_scenes),
            "scene_sequence": packed_scenes,
            "negative_prompt": self.build_negative_prompt(),
            "style_lock": self.BASE_STYLE,
            "character_lock": self.build_character_lock_block(),
            "location_lock": json.dumps(self.LOCATION_LOCK, ensure_ascii=False),
            "extra_notes": extra_notes or "Generate all scenes in one single batch in exact scene order. Keep visual continuity and character lock intact.",
        }

    def build_default_waterpark_story(self) -> Dict[str, Any]:
        scenes = [
            {
                "scene_number": 1,
                "title": "Water Park Shock",
                "description": "Pinki opens the door and freezes in comic surprise. The whole room has become a water park: cushion slide, shallow tub, bubbles, rubber duck. Kaavya on the left sits in a pink ring and smiles at the camera. Kaartik on the right sits in a yellow ring and grins with his teddy bear. Pinki looks shocked, dramatic, and funny.",
                "dialogue": "Pinki: 'Ye kya hai? Ghar mein water park?'",
                "duration_seconds": 8,
            },
            {
                "scene_number": 2,
                "title": "Plan Kya Tha",
                "description": "Kaavya is proud and bossy while Kaartik pours water into the tub. The teddy bear sits beside him. The room is warm, playful, and handmade like a tiny fantasy water park.",
                "dialogue": "Kaavya: 'Mumma, garmi bahut thi, isliye water park!' Kaartik: 'Main bhi!'",
                "duration_seconds": 8,
            },
            {
                "scene_number": 3,
                "title": "Engineer Kaavya",
                "description": "Kaavya acts like a tiny engineer with a toy helmet and directs the setup. Kaartik carries a colorful bucket and teddy clutched under his arm. They arrange the blue plastic sheet on the sofa slide and bubbles fill the room.",
                "dialogue": "Kaavya: 'Laddu, bucket idhar lao!'",
                "duration_seconds": 8,
            },
            {
                "scene_number": 4,
                "title": "Pehli Splash",
                "description": "Kaartik slides down the cushion in slow motion and splashes into the shallow tub. Water droplets sparkle in sunlight. Kaavya cheers and runs to the slide.",
                "dialogue": "Kaavya: 'Meri baari!'",
                "duration_seconds": 8,
            },
            {
                "scene_number": 5,
                "title": "Mummy Ka Twist",
                "description": "Pinki rushes in to stop them, slips on foam, and slides in slow motion into the tub with a funny cartoon splash. Kaavya and Kaartik burst into laughter.",
                "dialogue": "Pinki: 'HAI RAM!'",
                "duration_seconds": 8,
            },
            {
                "scene_number": 6,
                "title": "Mummy Bhi Shamil",
                "description": "Pinki sits in the tub laughing and splashes at the kids. Kaavya and Kaartik splash back. Teddy floats on the duck. Gentle joyful noise and warm family chaos.",
                "dialogue": "Pinki: 'Ab main bhi khelungi!' Kaartik: 'Mummy mast!'",
                "duration_seconds": 8,
            },
            {
                "scene_number": 7,
                "title": "Ab Saaf Kaun Karega",
                "description": "Wide shot. The room is full of water and bubbles. Pinki stands with wet dupatta, hands on hips, looking at the disaster. Kaavya points at Kaartik. Kaartik points at teddy. Freeze-frame comedy moment.",
                "dialogue": "Pinki: 'Ab saaf kaun karega?'",
                "duration_seconds": 8,
            },
            {
                "scene_number": 8,
                "title": "Like + Subscribe Outro",
                "description": "Front-facing eye-level shot. Kaavya points to a blue thumb icon and gives a thumbs-up. Kaartik hugs teddy and presses a glowing red SUBSCRIBE button. Pinki smiles and waves. Banner reads THE NAUGHTY DUO.",
                "dialogue": "Kaavya: 'Video pasand aaya to LIKE karo!' Kaartik: 'The Naughty Duo ko subscribe karo!' Pinki: 'Bell dabana mat bhoolna, naye video ke liye!'",
                "duration_seconds": 8,
            },
        ]

        return self.build_story_prompt_pack(
            title="Mummy Ghar Mein Water Park Dekh Ke Shock! 😱💦 Kaavya Aur Laddu Ki Shararat 😂",
            hook="The room turns into a tiny home water park and Pinki is stunned by the chaos.",
            scenes=scenes,
            extra_notes="Generate all 8 scenes in one batch in exact sequence. Keep scene flow, character identity, and room layout locked.",
        )

    def generate_daily_prompt_pack(self, concept_title: str, concept_hook: str, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.build_story_prompt_pack(title=concept_title, hook=concept_hook, scenes=scenes)
