import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

# Sample the most recent / important projects across the slots
TARGET_PROJECTS = [
    # Slot 0
    (0, "17d9a600-d978-4f15-a549-e6a4b271e629"),
    (0, "13f93410-698f-4e69-8e70-34c79b83ecb5"),
    (0, "1876f0f7-bc42-4764-86c9-35d76cb3a615"),
    # Slot 1
    (1, "28704e19-7200-4c0b-ab84-8e072ef4e201"),
    (1, "1fc9b4e8-54eb-4141-907d-77002b691fc7"),
    # Slot 2
    (2, "0fa549b9-b73f-4dac-8061-365fd0498eb2"),
    (2, "1fc877d7-73dd-4627-b635-df6b3549ee9e"),
    # Slot 3
    (3, "a1c6f19b-b046-41f3-9b33-fbc756646163"),
    # Slot 4
    (4, "c30fd23d-5a03-4081-baeb-fad9cbcc6a99"),
    # Slot 5
    (5, "3782c658-cb27-4a0a-b80b-db721a4ba00e"),
    # Slot 6
    (6, "11330d30-604f-4829-bb72-9d4f49e64a40"),
    # Slot 7
    (7, "642a9812-732d-411c-8bbe-380269736158")
]

def check_unharvested():
    results = []
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        for slot, pid in TARGET_PROJECTS:
            url = f"https://flow.google.com/u/{slot}/project/{pid}"
            print(f"\n--- Checking Slot {slot} Project {pid} ---")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(3500)

                # Count video elements / tiles
                videos = page.locator("video, [aria-label*='Open video in editor' i], flow-grid-tile-container, div.flow-grid-tile")
                v_count = videos.count()

                # Get title or prompt if visible
                title_el = page.locator("input[aria-label*='Project title' i], [class*='title'], h1, h2").first
                title = title_el.inner_text().strip() if title_el.count() > 0 else ""

                print(f"Slot {slot} | Project {pid} | Videos found: {v_count} | Title: {title}")
                results.append({
                    "slot": slot,
                    "pid": pid,
                    "url": url,
                    "videos_count": v_count,
                    "title": title
                })
            except Exception as e:
                print(f"Error checking {url}: {e}")

        ctx.close()

    with open("data/fleet_project_videos_overview.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    check_unharvested()
