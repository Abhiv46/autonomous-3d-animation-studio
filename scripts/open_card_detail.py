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
    
    # Click the first card
    cards = page.locator("div[role='button']")
    print("Cards found:", cards.count())
    if cards.count() > 0:
        card = cards.nth(2) # Top card
        print("Clicking card 2...")
        card.click(force=True)
        page.wait_for_timeout(3000)
        page.screenshot(path=str(BASE_DIR / "data" / "card_opened.png"))
        
        # Check buttons
        buttons = page.locator("button")
        print(f"Total buttons on page: {buttons.count()}")
        for i in range(buttons.count()):
            b = buttons.nth(i)
            if b.is_visible():
                txt = b.inner_text().strip()
                aria = b.get_attribute("aria-label") or ""
                if txt or aria:
                    print(f"Btn {i}: '{txt}' | aria: '{aria}'")

    ctx.close()
