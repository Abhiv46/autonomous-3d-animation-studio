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
    for slot in [1, 2]:
        url = f"https://flow.google.com/u/{slot}/"
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)
        shot = str(BASE_DIR / "data" / f"flow_slot_{slot}_home.png")
        page.screenshot(path=shot)
        print(f"Slot {slot} URL: {page.url}")
        print(f"Slot {slot} Screenshot saved: {shot}")
        # Look for project links
        for l in page.locator("a").all():
            try:
                href = l.get_attribute("href")
                if "project" in str(href):
                    print(f"Slot {slot} project link: {href}")
            except Exception:
                pass
        page.close()
    ctx.close()
