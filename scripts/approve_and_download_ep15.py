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

PROJECT_URL = "https://flow.google.com/u/6/project/480db28c-c470-46e0-9dac-f972c7a37e95"
BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
P1_OUT = RAW_CLIPS / "ep_15_fake_moustache_cop_p1.mp4"

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def approve_and_wait():
    print(f"[*] Navigating to active project: {PROJECT_URL}...", flush=True)
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
        page.wait_for_timeout(5000)

        # Click Always approve
        app_btn = page.locator("button:has-text('Always approve')").first
        if app_btn.count() == 0:
            app_btn = page.locator("button:has-text('Approve')").first

        if app_btn.count() > 0:
            print(f"[+] Found button: {app_btn.inner_text()}, clicking...", flush=True)
            app_btn.click(force=True)
            page.wait_for_timeout(3000)
            page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_approved_now.png")
            print("[+] Clicked approve! Saved screenshot to debug_approved_now.png", flush=True)

        # Wait for render (~65-75s)
        print("[*] Waiting for video render to finish (75s)...", flush=True)
        time.sleep(60)

        for attempt in range(10):
            cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video, div.flow-grid-tile")
            print(f"[*] Polling cards: found {cards.count()}...", flush=True)
            if cards.count() > 0:
                print("[+] Video card detected!", flush=True)
                break
            time.sleep(5)

        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_after_render.png")

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
                    print(f"[+] Downloading 720p to {P1_OUT.name}...", flush=True)
                    with page.expect_download(timeout=60000) as dl_info:
                        target_720.click(force=True)
                    dl = dl_info.value
                    dl.save_as(str(P1_OUT))
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(1000)
                    if P1_OUT.exists() and P1_OUT.stat().st_size > 1000000:
                        print(f"[SUCCESS] Scene 1 downloaded: {P1_OUT.name} ({P1_OUT.stat().st_size} bytes)", flush=True)
                        browser.close()
                        return True

        browser.close()
        return False

if __name__ == "__main__":
    approve_and_wait()
