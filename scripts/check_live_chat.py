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
    
    shot_path = str(BASE_DIR / "data" / "flow_live_chat_state.png")
    page.screenshot(path=shot_path)
    print("Screenshot saved to:", shot_path)
    
    # Check what is currently inside the prompt input box
    editor = page.locator("div.ProseMirror")
    if editor.count() > 0:
        print("Editor text inside:", repr(editor.first.inner_text()))
    
    # Check start generation button
    start_btn = page.locator("button[aria-label*='Start generation' i], button:has-text('arrow_forward')")
    print("Start button count:", start_btn.count())
    if start_btn.count() > 0:
        for idx in range(start_btn.count()):
            btn = start_btn.nth(idx)
            print(f"Button {idx}: is_visible={btn.is_visible()}, is_enabled={btn.is_enabled()}, aria='{btn.get_attribute('aria-label')}'")

    # Check for any alerts / modals / credit messages
    alerts = page.locator("[role='alert'], [role='dialog'], [class*='banner'], [class*='snack']").all()
    print("Alerts found:", len(alerts))
    for a in alerts:
        try:
            print("Alert text:", a.inner_text())
        except Exception:
            pass

    ctx.close()
