import os
import sys
import time
from playwright.sync_api import sync_playwright

PROJECT_URL = "https://flow.google.com/u/0/project/13f93410-698f-4e69-8e70-34c79b83ecb5"
BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def click_slot0_approve():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        page.goto(PROJECT_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        # Click Always approve by selector and coordinates
        opt = page.locator("div.option-row:has-text('Always approve')").first
        if opt.count() > 0:
            box = opt.bounding_box()
            print(f"[+] Bounding box: {box}")
            if box:
                page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                print("[+] Clicked center of Always approve!")
            else:
                opt.click(force=True)

        page.wait_for_timeout(3000)
        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_slot0_after_click.png")

        # Let's check text on page
        text = page.locator("body").inner_text()
        for line in text.split("\n"):
            if any(k in line.lower() for k in ["credit", "limit", "failed", "generating", "stop", "render"]):
                print(f"  [Status]: {line}")

        browser.close()

if __name__ == "__main__":
    click_slot0_approve()
