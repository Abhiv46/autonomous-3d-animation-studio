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
    
    # Click second session "Playful Pixar Style Story"
    # First click menu icon
    menu_icon = page.locator("button:has-text('menu'), [aria-label*='Sessions']").first
    if menu_icon.count() > 0:
        menu_icon.click(force=True)
        page.wait_for_timeout(1000)
        
        session2 = page.locator("text='Playful Pixar Style Story'").first
        if session2.count() > 0:
            print("Found session 2, clicking it!")
            session2.click(force=True)
            page.wait_for_timeout(3000)
            page.screenshot(path=str(BASE_DIR / "data" / "session2_view.png"))
            print("Session 2 screenshot saved!")
        else:
            print("Session 2 not found!")
    else:
        print("Menu icon not found!")

    ctx.close()
