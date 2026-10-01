import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent

brave_exe = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
brave_data = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

prompt_to_test = "Pixar 3D animated comedy. Modern Indian living room. Kaartik (5, yellow polo) holds toy game controller shouting Freeze! Pinki (25, powder-blue kurti) comically freezes carrying laundry. Kaavya (3, pink frock) giggles."

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
    
    # Target prompt editor inside flow-rich-text-editor
    editor = page.locator("flow-rich-text-editor div.ProseMirror")
    print("Editor count:", editor.count())
    editor.first.click()
    page.wait_for_timeout(400)
    
    # Type prompt
    page.keyboard.type(prompt_to_test, delay=5)
    page.wait_for_timeout(1000)
    
    arrow_btn = page.locator("button:has-text('arrow_forward')")
    print("Arrow btn enabled after typing:", arrow_btn.first.is_enabled())
    
    # Click arrow button
    arrow_btn.first.click(force=True)
    page.wait_for_timeout(5000)
    
    shot = str(BASE_DIR / "data" / "after_real_arrow_click.png")
    page.screenshot(path=shot)
    print("Screenshot after real arrow click:", shot)

    # Check button state now
    stop_btn = page.locator("button:has-text('Stop')")
    print("Is Stop button now visible:", stop_btn.count() > 0 and stop_btn.first.is_visible())

    ctx.close()
