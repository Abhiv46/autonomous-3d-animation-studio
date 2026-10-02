import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

SLOT_URL = "https://flow.google.com/u/1/"

P2_PROMPT = (
    "High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. "
    "Full 3D CGI animation. Bright sunlit modern kitchen of Indian home. "
    "Chubby toddler boy Kaartik (5 years old, bright yellow polo shirt, drawn black handlebar moustache on cheeks) "
    "playfully slams his small hand onto the clean kitchen counter, pointing his red magnifying glass at the high shelf cookie jar. "
    "Beside him, cute toddler sister Kaavya (3.5 years old, pink frock, double buns) blows through a straw making funny siren noises. "
    "Indian mother Pinki (25 years old, powder-blue kurti) drops her dish towel in dramatic theatrical surrender, "
    "raising both hands with wide playful eyes: 'Arre Inspector Sahab, hum nirdosh hain!' "
    "Vibrant Pixar 3D lighting, crisp CGI render, rich subsurface scattering. "
    "STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays."
)

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        print(f"[*] Checking Slot 1: {SLOT_URL}...")
        page.goto(SLOT_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        new_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i], div:has-text('New project')").first
        if new_btn.count() > 0 and new_btn.is_visible():
            new_btn.click(force=True)
            page.wait_for_timeout(5000)

        editor = page.locator("div.ProseMirror").first
        if editor.count() == 0:
            print("[-] Editor not found on Slot 1!")
            browser.close()
            return

        editor.click(force=True)
        page.wait_for_timeout(300)
        editor.fill(P2_PROMPT)
        page.wait_for_timeout(1000)

        start_btn = page.locator("button[aria-label*='Start generation' i]").first
        if start_btn.count() > 0:
            start_btn.click(force=True)
        else:
            page.keyboard.press("Enter")

        print("[*] Submitted prompt. Checking dialog/response...")
        for _ in range(15):
            opt = page.locator("div.option-row:has-text('Always approve'), span.option-label:has-text('Always approve'), div.option-row:has-text('Approve'), button:has-text('Always approve')").first
            if opt.count() > 0 and opt.is_visible():
                box = opt.bounding_box()
                if box:
                    page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                else:
                    opt.click(force=True)
                print("[+] Clicked Approval!")
                break
            time.sleep(2)

        time.sleep(10)
        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\slot1_test_submitted.png")
        browser.close()

if __name__ == "__main__":
    run()
