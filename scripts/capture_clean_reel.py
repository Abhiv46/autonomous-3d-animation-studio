import os
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

INSTA_URL = "https://www.instagram.com/reel/Dd4K6bCMu0D/"
BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def capture_clean_reel():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1400, "height": 950})

        page.goto(INSTA_URL, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)

        # Press Escape or click close button on the popup
        close_btn = page.locator("svg[aria-label='Close'], button[aria-label='Close'], div[role='dialog'] svg").first
        if close_btn.count() > 0:
            print("[+] Clicking Close button on modal...")
            close_btn.click()
        else:
            print("[+] Pressing Escape...")
            page.keyboard.press("Escape")

        page.wait_for_timeout(2000)

        # Take clean screenshot of video and stats
        page.screenshot(path="data/insta_reel_clean_frame.png")

        # Also let's check creator profile @your_favmochi to see exact video view count
        print("[*] Checking creator profile @your_favmochi for exact view counts...")
        page.goto("https://www.instagram.com/your_favmochi/reels/", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
        page.screenshot(path="data/insta_profile_reels.png")

        browser.close()

if __name__ == "__main__":
    capture_clean_reel()
