import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent

brave_exe = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
brave_data = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=brave_data,
        executable_path=brave_exe,
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    url = "https://flow.google.com/u/3/project/a1c6f19b-b046-41f3-9b33-fbc756646163"
    page = ctx.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(6000)
    
    shot_path = str(BASE_DIR / "data" / "flow_slot3_current_status.png")
    page.screenshot(path=shot_path)
    print("Screenshot saved to:", shot_path)
    
    # Check chat drawer texts
    messages = page.locator("[class*='message'], [class*='bubble'], p, [role='alert']").all()
    print("Found text elements in slot 3:", len(messages))
    for m in messages[-10:]:
        try:
            t = m.inner_text().strip()
            if len(t) > 5:
                print("Text:", t[:90])
        except Exception:
            pass

    # Check for videos or generation progress
    videos = page.locator("video, [aria-label*='video' i], [class*='generation-card']").all()
    print("Found video elements in slot 3:", len(videos))

    # Check bottom button (Start generation vs Stop)
    stop_btn = page.locator("button:has-text('Stop')")
    start_btn = page.locator("button[aria-label*='Start generation' i]")
    print("Is Stop button visible (actively generating):", stop_btn.count() > 0 and stop_btn.first.is_visible())
    print("Is Start generation button visible:", start_btn.count() > 0 and start_btn.first.is_visible())

    ctx.close()
