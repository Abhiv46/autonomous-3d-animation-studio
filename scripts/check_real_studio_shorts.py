import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def check_studio_shorts():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
        if skip.count() > 0 and skip.is_visible():
            skip.click()
            page.wait_for_timeout(4000)

        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\yt_studio_shorts_real_list.png")
        print("Real Shorts list captured.")
        browser.close()

if __name__ == "__main__":
    check_studio_shorts()
