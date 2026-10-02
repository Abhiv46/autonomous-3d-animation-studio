import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

# Videos to delete (duplicate uploads of Inspector Kaartik):
# 1. -aSuNsIxk_w (First upload with duplicate scene)
# 2. LgYQuo9lf3s (Second upload)
# Keep only the latest or check Studio content list

def manage_duplicates():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        print("[*] Opening YouTube Studio Content page...", flush=True)
        page.goto("https://studio.youtube.com/channel/UC/videos/short", wait_until="domcontentloaded")
        page.wait_for_timeout(5000)

        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\yt_studio_shorts_list.png")
        print(f"Current Studio URL: {page.url}", flush=True)
        browser.close()

if __name__ == "__main__":
    manage_duplicates()
