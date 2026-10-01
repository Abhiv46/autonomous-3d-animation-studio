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
    # Slot 2 (PRO slot with 500 credits)
    url = "https://flow.google.com/u/2/project/0fa549b9-b73f-4dac-8061-365fd0498eb2"
    page = ctx.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(6000)
    
    editor = page.locator("div.ProseMirror")
    print("Slot 2 editor visible:", editor.count() > 0 and editor.first.is_visible())
    if editor.count() > 0 and editor.first.is_visible():
        editor.first.click()
        page.keyboard.type(prompt_to_test, delay=5)
        page.wait_for_timeout(800)
        send_btn = page.locator("button[aria-label*='Start generation' i]")
        if send_btn.count() > 0 and send_btn.first.is_visible():
            send_btn.first.click(force=True)
            print("Successfully clicked Start generation on Slot 2 PRO account!")
            page.wait_for_timeout(4000)
    
    shot_path = str(BASE_DIR / "data" / "flow_slot2_dispatch.png")
    page.screenshot(path=shot_path)
    print("Saved screenshot to:", shot_path)
    ctx.close()
