import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
PROJECT_URL = "https://flow.google.com/u/4/project/5997b7be-97fa-431b-bd68-4428567b3a51"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=BRAVE_DATA,
        executable_path=BRAVE_EXE,
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = ctx.new_page()
    page.goto(PROJECT_URL, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(5000)
    page.screenshot(path=str(BASE_DIR / "data" / "slot4_current_project.png"))
    
    # Check text on page
    content = page.content()
    print("Page URL:", page.url)
    print("Has 'Freeze Mummy':", "Freeze Mummy" in content)
    print("Has video element:", page.locator("video").count())
    print("Has mat-card / tile:", page.locator("flow-grid-tile-container, mat-card, [role='article']").count())
    
    # Check chat / session drawer text
    texts = page.locator("p, span, div.message-content, [role='region']").all_inner_texts()
    relevant = [t.strip() for t in texts if any(w in t.lower() for w in ["freeze", "credit", "generating", "error", "video", "quota", "stop"])]
    print("Relevant texts found:", len(relevant))
    for r in relevant[:10]:
        print(" -", r[:80])
    ctx.close()
