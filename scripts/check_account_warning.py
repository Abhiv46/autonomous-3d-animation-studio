import os
import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def check_account_warning():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        page.goto("https://flow.google.com/u/7/", wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        # Hover or click on the avatar area (top right)
        avatar = page.locator("button[aria-label*='Google Account' i], img[alt*='Google Account' i], [aria-label*='profile' i]").first
        if avatar.count() > 0:
            print(f"[+] Found avatar: {avatar.get_attribute('aria-label')}")
            avatar.click(force=True)
            page.wait_for_timeout(2000)
            page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_avatar_popup.png")
            print("[+] Saved avatar popup screenshot")

        # Also let's check Slot 6 (which worked perfectly for Episode 17 earlier)
        print("[*] Checking Slot 6...")
        page.goto("https://flow.google.com/u/6/", wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_flow_slot6.png")
        print("[+] Slot 6 screenshot saved")

        browser.close()

if __name__ == "__main__":
    check_account_warning()
