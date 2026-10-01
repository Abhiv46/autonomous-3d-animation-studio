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
    for slot in range(3, 8):
        url = f"https://flow.google.com/u/{slot}/"
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3500)
        print(f"--- Slot {slot} ({page.url}) ---")
        # Check banner for credits
        banners = page.locator("[class*='banner'], [class*='alert']").all()
        for b in banners:
            try:
                t = b.inner_text().strip()
                if "credit" in t.lower():
                    print(f"Slot {slot} banner: {t[:60]}")
            except Exception:
                pass
        # Check project links
        for l in page.locator("a").all():
            try:
                href = l.get_attribute("href")
                if "project" in str(href):
                    print(f"Slot {slot} project: {href}")
            except Exception:
                pass
        page.close()
    ctx.close()
