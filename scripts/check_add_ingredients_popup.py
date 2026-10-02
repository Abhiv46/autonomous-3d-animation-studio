import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def check_add_menu():
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

        # Click the '+' button at bottom left of prompt bar (x=838, y=960 or similar)
        plus_btn = page.locator("button[aria-label*='Add' i], [aria-label*='ingredient' i], button:has-text('add')").last
        if plus_btn.count() > 0:
            plus_btn.click(force=True)
            page.wait_for_timeout(2000)
            page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\add_ingredients_popup.png")
            print("Popup captured!")

        browser.close()

if __name__ == "__main__":
    check_add_menu()
