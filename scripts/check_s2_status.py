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
    
    # 1. Open session 2 "Playful Pixar Style Story"
    menu_icon = page.locator("button:has-text('menu'), [aria-label*='Sessions']").first
    if menu_icon.count() > 0:
        menu_icon.click(force=True)
        page.wait_for_timeout(1000)
        s2 = page.locator("text='Playful Pixar Style Story'").first
        if s2.count() > 0:
            s2.click(force=True)
            page.wait_for_timeout(3000)
            
            # Read text in session 2
            text_s2 = page.locator("aside, [class*='drawer']").inner_text()
            print("Session 2 content:")
            print(text_s2)
            
    # 2. Check if Part 3 is done or still queueing
    page.screenshot(path=str(BASE_DIR / "data" / "session2_check_latest.png"))

    ctx.close()
