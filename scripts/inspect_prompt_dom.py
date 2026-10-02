import os
import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def inspect_prompt_dom():
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

        # Inspect all visible text inputs and textareas
        elements = page.evaluate('''() => {
            const results = [];
            document.querySelectorAll('textarea, input, [contenteditable="true"]').forEach(el => {
                const rect = el.getBoundingClientRect();
                results.push({
                    tag: el.tagName,
                    id: el.id,
                    className: el.className,
                    placeholder: el.getAttribute('placeholder'),
                    visible: rect.width > 0 && rect.height > 0,
                    rect: {x: rect.x, y: rect.y, w: rect.width, h: rect.height}
                });
            });
            return results;
        }''')
        print(f"[*] Found {len(elements)} input elements:")
        for el in elements:
            print(f"  {el}")

        browser.close()

if __name__ == "__main__":
    inspect_prompt_dom()
