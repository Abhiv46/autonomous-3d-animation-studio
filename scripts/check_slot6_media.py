import os
import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def check_slot6_home():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        page.goto("https://flow.google.com/u/6/", wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_slot6_home_now.png")
        print("[+] Saved slot6 home screenshot")

        # Also let's click the project "Oct 02 - 13:34"
        card = page.locator("text='Oct 02 - 13:34'").first
        if card.count() > 0:
            print("[+] Clicking Oct 02 - 13:34...")
            page.locator("a[href*='project']").first.click()
            page.wait_for_timeout(5000)
            page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_slot6_project_card.png")

            # Check All Media
            all_media = page.locator("button:has-text('All media'), div:has-text('All media')").first
            if all_media.count() > 0:
                all_media.click(force=True)
                page.wait_for_timeout(3000)
                page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_slot6_all_media.png")

        browser.close()

if __name__ == "__main__":
    check_slot6_home()
