import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.db.database import DatabaseManager

def seed_stories():
    catalog_path = Path("C:/TheNaughtyDuo_Automation/stories_catalog.json")
    if not catalog_path.exists():
        print(f"[!] Catalog not found: {catalog_path}")
        return

    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    db = DatabaseManager()
    seeded = 0
    skipped = 0

    for item in catalog:
        story_id = item.get("id")
        title = item.get("title")
        concept = item.get("description", title)
        
        # Build 3 parts
        parts = []
        if "part_1_prompt" in item:
            parts.append({"part_number": 1, "scene_label": "Hook", "prompt_text": item["part_1_prompt"]})
        if "part_2_prompt" in item:
            parts.append({"part_number": 2, "scene_label": "Prank/Climax", "prompt_text": item["part_2_prompt"]})
        if "part_3_prompt" in item:
            parts.append({"part_number": 3, "scene_label": "Resolution/Laugh", "prompt_text": item["part_3_prompt"]})

        if not parts:
            continue

        try:
            db.register_story(
                story_id=story_id,
                title=title,
                concept=concept[:200],
                structure="PROBLEM_ATTEMPT_PAYOFF",
                parts=parts,
                priority=2
            )
            print(f"[✓] Registered: {story_id} - '{title[:45]}...'")
            seeded += 1
        except ValueError as e:
            # Duplicate detection skipped it
            skipped += 1
            print(f"[-] Skipped duplicate: {story_id}")

    print(f"\n[SUMMARY] Successfully seeded {seeded} stories ({skipped} skipped).")

if __name__ == "__main__":
    seed_stories()
