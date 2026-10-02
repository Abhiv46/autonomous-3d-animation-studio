import os
import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
OUT_IMG = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_generation_started.png"

def trigger_generation():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        page.goto("https://flow.google.com/u/7/project/7a76f5b8-ef6f-448b-a37a-13999702619a", wait_until="domcontentloaded")
        page.wait_for_timeout(5000)

        # Click the start generation button
        start_btn = page.locator("button[aria-label*='Start generation' i], button:has-text('arrow_forward')").last
        if start_btn.count() > 0:
            print("[+] Clicking Start Generation button...")
            start_btn.click(force=True)
            page.wait_for_timeout(3000)

            # Check approvals
            for _ in range(5):
                app = page.locator("button:has-text('Always approve'), button:has-text('Approve')")
                if app.count() > 0 and app.last.is_visible():
                    print(f"[+] Found approval: {app.last.inner_text()}")
                    app.last.click(force=True)
                    page.wait_for_timeout(1000)
                    break
                time.sleep(1)

            page.wait_for_timeout(5000)
            page.screenshot(path=OUT_IMG)
            print(f"[+] Generation status screenshot saved to {OUT_IMG}")
        else:
            print("[-] Button not found!")

        browser.close()

if __name__ == "__main__":
    trigger_generation()
