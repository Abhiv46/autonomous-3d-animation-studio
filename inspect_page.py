import os
import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
VIDEO_ID = "k2JBp96Iqa4"

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=BRAVE_DATA,
        executable_path=BRAVE_EXE,
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.set_viewport_size({"width": 1600, "height": 1000})

    url = f"https://studio.youtube.com/video/{VIDEO_ID}/edit"
    print(f"[*] Navigating to {url}...")
    page.goto(url, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)

    print("Current URL:", page.url)
    print("Page Title:", page.title())

    page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_inspect.png")
    print("Saved inspection screenshot!")

    browser.close()
