import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

brave_exe = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
brave_data = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

project_id = "a2c6827b-3448-4a08-b05c-3a66b3ac48ec"
target_url = f"https://flow.google.com/u/0/project/{project_id}"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=brave_data,
        executable_path=brave_exe,
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = ctx.new_page()
    print("Navigating to:", target_url)
    page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(6000)
    
    screenshot_path = str(BASE_DIR / "data" / "flow_canvas_inspect.png")
    page.screenshot(path=screenshot_path)
    print("Saved screenshot to:", screenshot_path)
    
    # Check what selectors exist
    print("Page URL:", page.url)
    print("Title:", page.title())
    
    # Check prompt input selectors
    inputs = page.locator("textarea, [contenteditable='true'], div.ProseMirror, input").all()
    print("Found editable inputs:", len(inputs))
    for i, inp in enumerate(inputs[:5]):
        try:
            print(f"Input {i}: tag={inp.evaluate('el => el.tagName')}, class={inp.evaluate('el => el.className')}, placeholder={inp.get_attribute('placeholder')}")
        except Exception:
            pass

    # Check videos / cards
    cards = page.locator("[aria-label*='Open video in editor' i], video, [class*='card'], [class*='generation']").all()
    print("Found cards/videos:", len(cards))
    
    ctx.close()
