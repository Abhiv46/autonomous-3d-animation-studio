import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def inspect_characters():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        url0 = "https://flow.google.com/u/0/project/1876f0f7-bc42-4764-86c9-35d76cb3a615"
        page.goto(url0, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        # Click Characters tab
        char_btn = page.locator("[aria-label*='Characters' i], div:has-text('Characters')").first
        if char_btn.count() > 0:
            char_btn.click(force=True)
            page.wait_for_timeout(3000)
            page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\characters_library_view.png")
            print("Characters Library view captured.")

        browser.close()

if __name__ == "__main__":
    inspect_characters()
