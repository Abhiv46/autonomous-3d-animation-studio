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
    
    # 1. Close the right chat drawer by clicking the close button 'close'
    close_drawer_btn = page.locator("button[aria-label='Close'], button:has-text('close')").first
    if close_drawer_btn.count() > 0:
        print("Closing right drawer...")
        close_drawer_btn.click(force=True)
        page.wait_for_timeout(1000)
        
    page.screenshot(path=str(BASE_DIR / "data" / "drawer_closed.png"))
    print("Drawer closed screenshot saved!")
    
    # Check if more canvas cards are visible
    ctx.close()
