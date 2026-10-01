import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent

brave_exe = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
brave_data = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

target_url = "https://flow.google.com/u/0/project/1876f0f7-bc42-4764-86c9-35d76cb3a615"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=brave_data,
        executable_path=brave_exe,
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = ctx.new_page()
    page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(6000)
    
    shot_path = str(BASE_DIR / "data" / "flow_actual_project.png")
    page.screenshot(path=shot_path)
    print("Project screenshot:", shot_path)
    print("Page URL:", page.url)
    print("Title:", page.title())
    
    # Check title on page
    h_tags = page.locator("h1, h2, [class*='title'], [aria-label*='Project' i]").all()
    for h in h_tags[:5]:
        try:
            print("Element text:", h.inner_text())
        except Exception:
            pass

    ctx.close()
