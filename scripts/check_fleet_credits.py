import os
import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def check_all_slots_credits():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        for slot in [0, 4, 5, 1, 2, 3]:
            try:
                print(f"[*] Checking Slot {slot}...", flush=True)
                page.goto(f"https://flow.google.com/u/{slot}/", wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3000)

                # Check badges / PLUS
                plus = page.locator("text='PLUS', text='Plus', [aria-label*='Plus' i]")
                warn = page.locator("mat-icon:has-text('warning'), [aria-label*='warning' i]")
                print(f"  Slot {slot}: Plus badge={plus.count()}, Warning={warn.count()}")
                page.screenshot(path=f"C:\\TheNaughtyDuo_Automation\\the-naughty-duo-autonomous-content-engine\\data\\slot_{slot}_check.png")
            except Exception as e:
                print(f"  Slot {slot} error: {e}")

        browser.close()

if __name__ == "__main__":
    check_all_slots_credits()
