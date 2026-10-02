import os
import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
OUT_IMG = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_project_inside.png"

def open_card():
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

        # Find project cards
        cards = page.locator("a[href*='/project/'], [role='link'][href*='/project/'], flow-grid-tile, div[class*='project-card']")
        print(f"[*] Found {cards.count()} project links/cards")
        
        # Also find all <a> tags with project
        links = page.locator("a[href*='project']")
        print(f"[*] Found {links.count()} <a> links with project")
        if links.count() > 0:
            for i in range(min(5, links.count())):
                print(f"  Link {i}: {links.nth(i).get_attribute('href')}")
            print("[+] Clicking first project link...")
            links.first.click()
            page.wait_for_timeout(6000)
            print(f"[*] URL after click: {page.url}")
            page.screenshot(path=OUT_IMG)
        else:
            # Click near top-left of the first tile: x=170, y=550
            print("[+] Clicking coordinates of first project tile...")
            page.mouse.click(170, 550)
            page.wait_for_timeout(6000)
            print(f"[*] URL after coordinate click: {page.url}")
            page.screenshot(path=OUT_IMG)

        browser.close()

if __name__ == "__main__":
    open_card()
