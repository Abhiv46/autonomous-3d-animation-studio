import os
import sys
import time
from playwright.sync_api import sync_playwright

PROJECT_URL = "https://flow.google.com/u/6/project/480db28c-c470-46e0-9dac-f972c7a37e95"
BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def inspect_approve():
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

        info = page.evaluate('''() => {
            const results = [];
            document.querySelectorAll('*').forEach(el => {
                const txt = el.innerText ? el.innerText.trim() : '';
                if (txt === 'Approve' || txt === 'Always approve' || txt.includes('Always approve')) {
                    const rect = el.getBoundingClientRect();
                    results.push({
                        tag: el.tagName,
                        className: el.className,
                        text: txt,
                        rect: {x: rect.x, y: rect.y, w: rect.width, h: rect.height}
                    });
                }
            });
            return results;
        }''')
        print(f"[*] Found {len(info)} elements matching Approve:")
        for item in info:
            print(f"  {item}")

        browser.close()

if __name__ == "__main__":
    inspect_approve()
