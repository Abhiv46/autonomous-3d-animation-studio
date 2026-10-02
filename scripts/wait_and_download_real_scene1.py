import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
RAW_CLIPS.mkdir(parents=True, exist_ok=True)

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

PROJECT_URL = "https://flow.google.com/u/4/project/5997b7be-97fa-431b-bd68-4428567b3a51"
OUT_VIDEO_PATH = RAW_CLIPS / "ep_18_scene_01_real.mp4"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=BRAVE_DATA,
        executable_path=BRAVE_EXE,
        headless=True,
        accept_downloads=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = ctx.new_page()
    print(f"[*] Connecting to active project: {PROJECT_URL}...", flush=True)
    page.goto(PROJECT_URL, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(4000)

    # Monitor generation loop (up to 3 minutes)
    for i in range(36):
        time.sleep(5)
        # Check if approval button is shown
        app_btn = page.locator("button:has-text('Approve'), button:has-text('Always approve')")
        if app_btn.count() > 0 and app_btn.first.is_visible():
            print("[+] Approving prompt generation...", flush=True)
            app_btn.first.click(force=True)
            page.wait_for_timeout(2000)

        # Check if video tile or cards appeared
        tiles = page.locator("flow-grid-tile-container, [aria-label*='Open video in editor' i], mat-card")
        stop_btn = page.locator("button:has-text('Stop'), button[aria-label='Stop']")
        is_rendering = stop_btn.count() > 0 and stop_btn.first.is_visible()
        
        print(f"[*] Loop {i+1}/36: Tiles found: {tiles.count()} | Rendering: {is_rendering}", flush=True)

        if tiles.count() > 0 and not is_rendering:
            print("[🎉] Video tile rendered successfully!", flush=True)
            page.screenshot(path=str(BASE_DIR / "data" / "scene1_rendered_canvas.png"))
            break

    page.screenshot(path=str(BASE_DIR / "data" / "scene1_final_check.png"))
    ctx.close()
