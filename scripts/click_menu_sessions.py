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
    
    # Click menu button to list chat sessions
    menu_icon = page.locator("button:has-text('menu'), [aria-label*='Sessions'], [aria-label*='History']").first
    if menu_icon.count() > 0:
        print("Clicking menu icon...")
        menu_icon.click(force=True)
        page.wait_for_timeout(2000)
        page.screenshot(path="data/sessions_menu_open.png")
        
        # Print list of sessions
        session_items = page.locator("mat-nav-list a, [role='listitem'], div[class*='session-item'], [role='menuitem']")
        print(f"Session items count: {session_items.count()}")
        for i in range(session_items.count()):
            print(f"Session {i}: {session_items.nth(i).inner_text()}")

    ctx.close()
