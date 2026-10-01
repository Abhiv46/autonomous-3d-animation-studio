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
    url = "https://flow.google.com/u/3/project/a1c6f19b-b046-41f3-9b33-fbc756646163"
    page = ctx.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(6000)
    
    # 1. Switch to Session 1 "Playful Indian Family Game" where our Freeze remote prompt was typed!
    menu_icon = page.locator("button:has-text('menu'), [aria-label*='Sessions']").first
    if menu_icon.count() > 0:
        menu_icon.click(force=True)
        page.wait_for_timeout(1000)
        s1 = page.locator("text='Playful Indian Family Game'").first
        if s1.count() > 0:
            s1.click(force=True)
            page.wait_for_timeout(3000)
            
    # Check bottom of chat drawer in Session 1
    page.screenshot(path=str(BASE_DIR / "data" / "session1_current_state.png"))
    print("Screenshot saved to data/session1_current_state.png")
    
    # Check stop button or any message
    stop_btn = page.locator("button:has-text('Stop')")
    print("Stop button present in S1:", stop_btn.count() > 0 and stop_btn.first.is_visible())
    
    # Look for any text inside the drawer
    chat_container = page.locator("flow-chat-panel, div[class*='chat-content'], div[class*='messages']").first
    if chat_container.count() > 0:
        print("Chat content:")
        print(chat_container.inner_text())

    ctx.close()
