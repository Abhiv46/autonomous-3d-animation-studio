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
    
    # Check bottom area elements
    bottom_area = page.locator("[class*='input'], [class*='bottom'], [class*='footer']").all()
    print("Bottom containers found:", len(bottom_area))
    for b in bottom_area[-5:]:
        try:
            print("Tag:", b.evaluate("el => el.tagName"), "Class:", b.evaluate("el => el.className"))
        except Exception:
            pass

    # Find the right arrow icon at the bottom right
    arrows = page.locator("button:has-text('arrow_forward'), [aria-label*='generate' i], [aria-label*='send' i]").all()
    print("Arrow buttons count:", len(arrows))
    for arr in arrows:
        try:
            print("Arrow btn: aria='", arr.get_attribute("aria-label"), "' text='", arr.inner_text(), "' enabled=", arr.is_enabled())
        except Exception:
            pass

    ctx.close()
