import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def inspect_character_cards():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        url2 = "https://flow.google.com/u/2/project/0fa549b9-b73f-4dac-8061-365fd0498eb2"
        page.goto(url2, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        # Click on Kaartik character card
        kaartik = page.locator("text='Kaartik'").last
        if kaartik.count() > 0:
            kaartik.click(force=True)
            page.wait_for_timeout(2000)
            page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\kaartik_modal_opened.png")
            print("Kaartik card clicked, screenshot saved.")

        browser.close()

if __name__ == "__main__":
    inspect_character_cards()
