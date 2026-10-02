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
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = b.pages[0] if b.pages else b.new_page()
    page.set_viewport_size({"width": 1440, "height": 900})
    
    # Go directly to YouTube Studio upload
    page.goto('https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiYF480ioLg', wait_until='domcontentloaded', timeout=40000)
    page.wait_for_timeout(4000)
    
    skip = page.get_by_text("SKIP TO YOUTUBE STUDIO")
    if skip.count() > 0:
        print("Clicking SKIP TO YOUTUBE STUDIO...")
        skip.first.click()
        page.wait_for_timeout(6000)
        
    print("Page URL:", page.url)
    page.screenshot(path='data/yt_studio_channel_page.png')
    
    # Check for upload button: #create-icon, button#upload-button, [aria-label*='Create' i]
    create_btn = page.locator("#create-icon, button[aria-label*='Create' i], ytcp-button:has-text('CREATE')")
    print("Create button count:", create_btn.count())
    
    b.close()
