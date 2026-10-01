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
    
    # Hover over card 2 to reveal overlay icons
    cards = page.locator("div[role='button']")
    card = cards.nth(2)
    card.hover()
    page.wait_for_timeout(1000)
    
    # Look for "more_vert" button on the hovered card
    more_btn = page.locator("button[aria-label='More options']").first
    if more_btn.count() > 0:
        print("Clicking more options on card...")
        more_btn.click(force=True)
        page.wait_for_timeout(1500)
        page.screenshot(path=str(BASE_DIR / "data" / "card_menu_open.png"))
        
        # Check menu items
        menu_items = page.locator("[role='menuitem'], mat-menu-item, button")
        for i in range(menu_items.count()):
            txt = menu_items.nth(i).inner_text().strip()
            if any(w in txt.lower() for w in ['download', 'export', 'open', 'details', 'info']):
                print(f"Found option: {txt}")

    ctx.close()
