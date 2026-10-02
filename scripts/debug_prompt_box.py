import os
import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
OUT_IMG = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_prompt_box.png"

def test_prompt_box():
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

        # Check the warning icon on top right
        warn = page.locator("mat-icon:has-text('warning'), [aria-label*='warning' i], .warning-icon, button:has-text('warning')")
        print(f"[*] Warning icons found: {warn.count()}")
        if warn.count() > 0:
            for i in range(warn.count()):
                try:
                    txt = warn.nth(i).inner_text()
                    aria = warn.nth(i).get_attribute("aria-label")
                    print(f"  Warn {i}: text='{txt}', aria='{aria}'")
                except:
                    pass

        # Check credits / plan
        body_text = page.locator("body").inner_text()
        for line in body_text.split("\n"):
            if any(k in line.lower() for k in ["credit", "limit", "quota", "plan", "upgrade", "wait"]):
                print(f"  [Text Match]: {line}")

        # Check prompt box
        inp = page.locator("[contenteditable='true'], div.ProseMirror, textarea, input[placeholder*='create' i]")
        print(f"[*] Input elements found: {inp.count()}")
        if inp.count() > 0:
            target_inp = inp.last
            target_inp.click()
            page.wait_for_timeout(500)
            target_inp.fill("Test prompt 3D Pixar animation of happy toddler")
            page.wait_for_timeout(1000)
            page.screenshot(path=OUT_IMG)
            print(f"[+] Typed test prompt and saved screenshot to {OUT_IMG}")

        browser.close()

if __name__ == "__main__":
    test_prompt_box()
