import os
import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
OUT_IMG = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_prompt_typed.png"

def test_submission():
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

        editor = page.locator("div.ProseMirror").first
        if editor.count() > 0:
            print("[+] Found div.ProseMirror!")
            editor.click()
            page.wait_for_timeout(500)
            editor.fill("Vertical 9:16 aspect ratio, 8 seconds. CoComelon meets Pixar 3D animated style for toddlers. Kaartik wearing yellow polo marches proudly in sunny kitchen with drawn black moustache blowing a whistle.")
            page.wait_for_timeout(1000)

            # Find send button
            btns = page.evaluate('''() => {
                const results = [];
                document.querySelectorAll('button').forEach(b => {
                    const rect = b.getBoundingClientRect();
                    results.push({
                        text: b.innerText.trim(),
                        aria: b.getAttribute('aria-label'),
                        visible: rect.width > 0 && rect.height > 0,
                        rect: {x: rect.x, y: rect.y, w: rect.width, h: rect.height}
                    });
                });
                return results;
            }''')
            print(f"[*] Found {len(btns)} buttons:")
            for b in btns:
                if b['rect']['y'] > 800:
                    print(f"  Bottom button: {b}")

            page.screenshot(path=OUT_IMG)
            print(f"[+] Screenshot saved to {OUT_IMG}")

        browser.close()

if __name__ == "__main__":
    test_submission()
