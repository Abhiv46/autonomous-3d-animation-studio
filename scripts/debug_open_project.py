import os
import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
OUT_IMG = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_project_1319.png"

def open_project():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        print("[*] Opening Slot 7 project page...")
        page.goto("https://flow.google.com/u/7/", wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        # Click the project card
        card = page.locator("text='Oct 02 - 13:19'").first
        if card.count() > 0:
            print("[+] Clicking Oct 02 - 13:19 card...")
            card.click(force=True)
            page.wait_for_timeout(6000)
            print(f"[*] Current URL: {page.url}")
            page.screenshot(path=OUT_IMG)
            print(f"[+] Saved project screenshot to {OUT_IMG}")
        else:
            print("[-] Card not found!")

        browser.close()

if __name__ == "__main__":
    open_project()
