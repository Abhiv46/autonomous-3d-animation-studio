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
    
    # Check if there is a session dropdown or list
    # The header shows "Playful Indian Family Game" with an edit icon and close icon
    # Let's inspect elements in that panel
    print("Page title:", page.title())
    
    # Find all text in the right sidebar
    texts = page.locator("aside, [class*='drawer'], [class*='sidebar'], [class*='panel']").all_inner_texts()
    print("Sidebar texts:", len(texts))
    for t in texts[:5]:
        print("--- SIDEBAR BLOCK ---")
        print(t[:200])

    # Also check if clicking on the history or session menu reveals older chats
    menu_icon = page.locator("button:has-text('menu'), [aria-label*='Sessions'], [aria-label*='History']").first
    if menu_icon.count() > 0:
        print("Menu icon found!")
        
    page.screenshot(path="data/live_check_drawer.png")
    print("Screenshot saved to data/live_check_drawer.png")
    ctx.close()
