import os
import sys
import time
import json
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

def open_reel():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 900})

        print("[*] Navigating to reel...")
        page.goto(INSTA_URL, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)

        # Check for Continue button
        btn = page.locator("button:has-text('Continue'), a:has-text('Continue'), div[role='button']:has-text('Continue')").first
        if btn.count() > 0 and btn.is_visible():
            print("[+] Found 'Continue' button for r_e_e_n_a_c_h_d, clicking...")
            btn.click()
            page.wait_for_timeout(6000)

        # In case it redirected to home, go back to reel URL
        if "reel" not in page.url:
            print(f"[*] Navigating back to {INSTA_URL} after session refresh...")
            page.goto(INSTA_URL, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(5000)

        # Screenshot the reel page
        page.screenshot(path="data/insta_reel_loaded.png")
        print(f"[+] Current URL: {page.url}")

        # Capture text and elements
        body = page.locator("body").inner_text()
        print("[+] Body preview:\n", body[:1000])

        # Search for likes, views, creator username
        with open("data/insta_reel_text.txt", "w", encoding="utf-8") as f:
            f.write(body)

        # Also get any video urls
        videos = page.locator("video").all()
        print(f"[+] Found {len(videos)} video elements")
        for idx, v in enumerate(videos):
            src = v.get_attribute("src") or ""
            print(f"  Video {idx} src: {src[:100]}...")

        browser.close()

if __name__ == "__main__":
    open_reel()
