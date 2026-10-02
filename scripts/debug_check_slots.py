import os
import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
OUT_IMG_7 = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_flow_slot7.png"
OUT_IMG_5 = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_flow_slot5.png"

def check_slots():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        print("[*] Checking Slot 7...")
        page.goto("https://flow.google.com/u/7/", wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        page.screenshot(path=OUT_IMG_7)
        print(f"[+] Slot 7 saved to {OUT_IMG_7}")

        print("[*] Checking Slot 5...")
        page.goto("https://flow.google.com/u/5/", wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        page.screenshot(path=OUT_IMG_5)
        print(f"[+] Slot 5 saved to {OUT_IMG_5}")

        browser.close()

if __name__ == "__main__":
    check_slots()
