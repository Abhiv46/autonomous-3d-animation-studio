import os
import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

with sync_playwright() as p:
    b = p.chromium.launch_persistent_context(
        user_data_dir=BRAVE_DATA,
        executable_path=BRAVE_EXE,
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = b.pages[0] if b.pages else b.new_page()
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto('https://studio.youtube.com/', wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(4000)
    
    # Click "SKIP TO YOUTUBE STUDIO"
    skip = page.locator("text=SKIP TO YOUTUBE STUDIO, button:has-text('SKIP')")
    if skip.count() > 0:
        print("Clicking SKIP TO YOUTUBE STUDIO...")
        skip.first.click()
        page.wait_for_timeout(6000)
        
    print("Page URL after skip:", page.url)
    page.screenshot(path='data/yt_studio_dashboard.png')
    
    # Check current channel name
    body = page.locator("body").inner_text()
    for line in body.split("\n"):
        ln = line.strip()
        if any(w in ln.lower() for w in ["naughty", "duo", "subscribers", "upload", "channel"]):
            print(f"Channel text: {ln}")
            
    b.close()
