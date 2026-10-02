import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_URL = "https://flow.google.com/u/6/project/a893396b-c49b-4159-9526-39b746866334"
BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
P1_FILE = RAW_CLIPS / "ep_15_fake_moustache_cop_p1.mp4"

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def download_rendered_scene1():
    print(f"[*] Connecting to active project: {PROJECT_URL}...", flush=True)
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

        page.goto(PROJECT_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(6000)

        # Wait for video card / completion
        for check in range(12):
            # Check if stop button is gone and video card exists
            stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
            cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video, div.video-card")
            print(f"[*] Check {check+1}: Stop btn={stop_btn.count()}, Cards={cards.count()}", flush=True)

            if stop_btn.count() == 0 and cards.count() > 0:
                print("[+] Render completed! Opening video card...", flush=True)
                break
            time.sleep(6)

        scr_check = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_scene1_completed.png"
        page.screenshot(path=scr_check)
        print(f"[+] Screenshot saved to {scr_check}", flush=True)

        # Download video
        cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video")
        if cards.count() > 0:
            cards.last.click(force=True)
            page.wait_for_timeout(2500)
            dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
            if dl_btn.count() > 0 and dl_btn.is_visible():
                dl_btn.click(force=True)
                page.wait_for_timeout(1500)
                target_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size')").first
                if target_720.count() > 0:
                    print(f"[+] Triggering 720p download to {P1_FILE.name}...", flush=True)
                    with page.expect_download(timeout=60000) as dl_info:
                        target_720.click(force=True)
                    dl = dl_info.value
                    dl.save_as(str(P1_FILE))
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(1000)
                    if P1_FILE.exists() and P1_FILE.stat().st_size > 1000000:
                        print(f"[SUCCESS] Scene 1 Saved: {P1_FILE.name} ({P1_FILE.stat().st_size} bytes)", flush=True)
                        browser.close()
                        return True

        browser.close()
        return False

if __name__ == "__main__":
    download_rendered_scene1()
