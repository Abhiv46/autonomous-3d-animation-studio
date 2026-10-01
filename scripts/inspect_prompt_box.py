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
    page.wait_for_timeout(5000)
    
    # Check elements on right drawer
    placeholder = page.locator("[placeholder*='What do you want to create' i], textarea, [contenteditable='true']").all()
    print("Found prompt inputs matching placeholder:", len(placeholder))
    for i, p_loc in enumerate(placeholder):
        try:
            print(f"Match {i}: tag={p_loc.evaluate('el => el.tagName')}, class={p_loc.evaluate('el => el.className')}, placeholder={p_loc.get_attribute('placeholder')}")
        except Exception:
            pass

    # Check button near it
    btns = page.locator("button").all()
    print("Found buttons count:", len(btns))
    for b in btns:
        try:
            aria = b.get_attribute("aria-label") or ""
            text = b.inner_text() or ""
            if any(x in (aria + text).lower() for x in ["send", "arrow", "create", "generate", "submit"]):
                print(f"Candidate submit button: aria='{aria}', text='{text}'")
        except Exception:
            pass

    ctx.close()
