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
    page.wait_for_timeout(7000)
    
    shot = str(BASE_DIR / "data" / "live_slot3_check.png")
    page.screenshot(path=shot)
    print("Screenshot:", shot)
    
    # Check for videos, stop button, cards, etc.
    videos = page.locator("video")
    print(f"Videos count: {videos.count()}")
    for i in range(videos.count()):
        print(f"Video {i} src: {videos.nth(i).get_attribute('src')}")
        
    stop_btn = page.locator("button:has-text('Stop')")
    print(f"Stop button visible: {stop_btn.count() > 0 and stop_btn.first.is_visible()}")
    
    # Look for video thumbnails or media cards
    cards = page.locator("[aria-label*='Open video in editor' i], [aria-label*='Play video' i]")
    print(f"Video cards count: {cards.count()}")
    
    # Look for progress indicators or text
    body_text = page.locator("body").inner_text()
    for line in body_text.split("\n"):
        ln = line.strip()
        if any(w in ln.lower() for w in ["generating", "error", "failed", "freeze", "remote", "credit", "limit"]):
            print(f"Relevant line: {ln}")

    ctx.close()
