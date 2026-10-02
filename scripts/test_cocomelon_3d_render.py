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

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
RAW_CLIPS.mkdir(parents=True, exist_ok=True)

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

COCOMELON_3D_PROMPT = (
    "CoComelon and Pixar 3D animated style, 9:16 vertical orientation, 8 seconds. "
    "Full 3D CGI render, ultra-high quality 3D character models with smooth rounded features, "
    "big expressive glassy 3D eyes, volumetric 3D hair with glossy highlights. "
    "In a bright, sunny modern Indian living room with warm golden sunlight: "
    "5-year-old cute Indian boy Kaartik (chubby cheeks, vibrant yellow polo) and "
    "adorable 3-year-old toddler sister Kaavya (candy pink frock, two bouncy double buns) "
    "are playing happily. Rich 3D textures, soft ambient occlusion, cinematic volumetric studio lighting, "
    "Pixar Disney 3D animation, CoComelon toddler aesthetic, NO 2D drawing, NO flat sketch, NO speech bubbles."
)

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=BRAVE_DATA,
        executable_path=BRAVE_EXE,
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = ctx.new_page()
    print("[*] Navigating to Google Flow Slot 4...", flush=True)
    page.goto("https://flow.google.com/u/4/", wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(3000)

    # Click "+ New project"
    new_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i]").first
    if new_btn.count() > 0 and new_btn.is_visible():
        new_btn.click()
        page.wait_for_timeout(4000)

    # Submit 3D CGI prompt
    editor = page.locator("[contenteditable='true'], div.ProseMirror, textarea").first
    print("[*] Typing CoComelon 3D CGI prompt into editor...", flush=True)
    editor.click()
    page.wait_for_timeout(300)
    editor.fill(COCOMELON_3D_PROMPT)
    page.wait_for_timeout(500)

    send_btn = page.locator("button:has-text('arrow_forward'), button[aria-label*='Submit' i], button.send-button").first
    if send_btn.count() > 0 and send_btn.is_visible():
        send_btn.click()
    else:
        page.keyboard.press("Enter")

    print("[🚀] Prompt sent! Waiting 35s for generation...", flush=True)
    time.sleep(35)

    page.screenshot(path=str(BASE_DIR / "data" / "cocomelon_3d_test_result.png"))
    print("[✓] Screenshot saved to data/cocomelon_3d_test_result.png!")
    ctx.close()
