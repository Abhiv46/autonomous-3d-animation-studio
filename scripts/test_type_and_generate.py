import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent

brave_exe = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
brave_data = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
target_url = "https://flow.google.com/u/0/project/1876f0f7-bc42-4764-86c9-35d76cb3a615"

prompt_to_test = "Pixar 3D animated comedy. Modern Indian living room. Kaartik (5, yellow polo) holds toy game controller shouting Freeze! Pinki (25, powder-blue kurti) comically freezes carrying laundry. Kaavya (3, pink frock) giggles."

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
    
    # 1. Click prompt editor
    editor = page.locator("div.ProseMirror")
    print("Editor visible:", editor.first.is_visible())
    editor.first.click()
    page.wait_for_timeout(300)
    
    # Type prompt using keyboard
    page.keyboard.type(prompt_to_test, delay=10)
    page.wait_for_timeout(1000)
    
    start_btn = page.locator("button[aria-label*='Start generation' i]")
    print("Start button enabled after typing:", start_btn.is_enabled())
    
    # Click start button
    start_btn.click(force=True)
    page.wait_for_timeout(3000)
    
    shot_after = str(BASE_DIR / "data" / "after_click_generate.png")
    page.screenshot(path=shot_after)
    print("Screenshot saved to:", shot_after)

    ctx.close()
