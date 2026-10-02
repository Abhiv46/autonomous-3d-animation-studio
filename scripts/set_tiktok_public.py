import os
import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def set_ep17_public():
    print("[*] Launching Brave to set Episode 17 to Public...")
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1440, "height": 900})
        page.goto("https://www.tiktok.com/tiktokstudio/content", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(6000)
        
        # Look for Private dropdown button
        priv_btns = page.locator("button:has-text('Private'), div:has-text('Private')")
        print(f"[*] Found {priv_btns.count()} elements with 'Private'")
        
        # Target the dropdown in the row
        dropdown_btn = page.locator("[data-e2e='privacy-select'], button:has-text('Private')").first
        if dropdown_btn.count() > 0 and dropdown_btn.is_visible():
            print("[+] Clicking Private dropdown...")
            dropdown_btn.click(force=True)
            page.wait_for_timeout(1500)
            
            # Select Public option
            public_opt = page.locator("li:has-text('Public'), div:has-text('Public'), [role='option']:has-text('Public')").first
            if public_opt.count() > 0 and public_opt.is_visible():
                print("[+] Clicking 'Public' option...")
                public_opt.click(force=True)
                page.wait_for_timeout(2000)
            else:
                print("[!] Public option not visible, checking page text...")
                
        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\tiktok_ep17_public_check.png")
        browser.close()
        print("[✓] Checked privacy setting.")

if __name__ == "__main__":
    set_ep17_public()
