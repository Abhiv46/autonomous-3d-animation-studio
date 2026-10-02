import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def open_canvas():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            accept_downloads=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})
        page.goto("https://flow.google.com/u/1/", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        
        card = page.locator("text='Oct 02 - 14:11'").first
        if card.count() > 0:
            print("Found text selector, clicking...", flush=True)
            card.click(force=True)
        else:
            print("Clicking (335, 600)...", flush=True)
            page.mouse.click(335, 600)
            
        page.wait_for_timeout(6000)
        print(f"Canvas URL: {page.url}", flush=True)
        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\slot1_canvas_inside.png")
        browser.close()

if __name__ == "__main__":
    open_canvas()
