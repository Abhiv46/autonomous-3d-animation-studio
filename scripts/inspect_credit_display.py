import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def inspect_credits_screen():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        # Test on Slot 0 first
        page.goto("https://flow.google.com/u/0/", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        # Check gear icon or profile icon
        gear = page.locator("button[aria-label*='Settings' i], button[aria-label*='settings' i], button:has-text('settings')").first
        if gear.count() > 0:
            print("Clicking settings gear...")
            gear.click(force=True)
            page.wait_for_timeout(2000)
            page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\slot0_settings_modal.png")

        # Check avatar
        avatar = page.locator("button[aria-label*='Google Account' i], img[alt*='Google Account' i]").first
        if avatar.count() > 0:
            print("Clicking avatar...")
            avatar.click(force=True)
            page.wait_for_timeout(2000)
            page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\slot0_avatar_popup.png")

        browser.close()

if __name__ == "__main__":
    inspect_credits_screen()
