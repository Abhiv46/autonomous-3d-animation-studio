import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_URL = "https://flow.google.com/u/0/project/1876f0f7-bc42-4764-86c9-35d76cb3a615"
BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def check_and_download():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            accept_downloads=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        page.goto(PROJECT_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        # Ensure on canvas
        back_btn = page.locator("button[aria-label*='back' i]").first
        if back_btn.count() > 0 and back_btn.is_visible():
            back_btn.click(force=True)
            page.wait_for_timeout(2000)

        page.screenshot(path="data/ep20_canvas_overview.png")

        tiles = page.locator("flow-grid-tile-container, div.flow-grid-tile, [aria-label*='video' i]").all()
        print(f"Total tiles found: {len(tiles)}")
        for idx, t in enumerate(tiles[:8]):
            aria = t.get_attribute("aria-label") or ""
            txt = t.inner_text().strip().replace("\n", " ")
            print(f"Tile {idx}: aria='{aria}' text='{txt[:50]}'")

        browser.close()

if __name__ == "__main__":
    check_and_download()
