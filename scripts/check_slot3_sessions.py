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
    
    # Click hamburger menu or sessions button in right drawer top-left
    session_btn = page.locator("[aria-label*='session' i], [aria-label*='history' i], button:has-text('menu'), button:has-text('Untitled session')").all()
    print("Session buttons found:", len(session_btn))
    for sb in session_btn[:5]:
        try:
            print("Session btn text:", sb.inner_text(), "aria:", sb.get_attribute("aria-label"))
        except Exception:
            pass

    # Look for the hamburger icon on top left of drawer (three horizontal lines)
    hamburger = page.locator("button:has-text('menu'), button:has-text('dehaze'), [aria-label*='Sessions' i], [aria-label*='chats' i]")
    print("Hamburger count:", hamburger.count())
    if hamburger.count() > 0:
        hamburger.first.click()
        page.wait_for_timeout(2000)
        shot = str(BASE_DIR / "data" / "flow_slot3_sessions_opened.png")
        page.screenshot(path=shot)
        print("Opened sessions menu screenshot:", shot)
        # List sessions
        items = page.locator("[role='menuitem'], [class*='session-item'], [class*='chat-item'], div:has-text('Untitled session')").all()
        print("Session list items:", len(items))
        for it in items[:5]:
            try:
                print("Item:", it.inner_text())
            except Exception:
                pass

    ctx.close()
