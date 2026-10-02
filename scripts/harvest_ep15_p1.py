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

PROJECT_URL = "https://flow.google.com/u/6/project/38e31ef9-3d24-4ba6-a035-ad9e27c4142c"
BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
P1_FILE = RAW_CLIPS / "ep_15_fake_moustache_cop_p1.mp4"

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def click_and_harvest():
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
        page.wait_for_timeout(4000)

        # Click Always approve
        opt = page.locator("div.option-row:has-text('Always approve'), span.option-label:has-text('Always approve')").first
        if opt.count() > 0:
            print("[+] Clicking 'Always approve' on the 10-credit dialog...", flush=True)
            opt.click(force=True)
            page.wait_for_timeout(3000)
        else:
            app = page.locator("div.option-row:has-text('Approve'), span.option-label:has-text('Approve')").first
            if app.count() > 0:
                print("[+] Clicking 'Approve'...", flush=True)
                app.click(force=True)
                page.wait_for_timeout(3000)

        # Keep browser open and wait for render
        print("[*] Waiting for video render (~70s)...", flush=True)
        time.sleep(60)

        for attempt in range(15):
            cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video")
            print(f"[*] Check {attempt+1}: found {cards.count()} cards...", flush=True)
            if cards.count() > 0:
                print("[+] Video rendered on canvas!", flush=True)
                break
            time.sleep(5)

        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_rendered_success.png")

        # Download 720p
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
                    print(f"[+] Triggering 720p download -> {P1_FILE.name}...", flush=True)
                    with page.expect_download(timeout=60000) as dl_info:
                        target_720.click(force=True)
                    dl = dl_info.value
                    dl.save_as(str(P1_FILE))
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(1000)
                    if P1_FILE.exists() and P1_FILE.stat().st_size > 1000000:
                        print(f"[🏆 SAVED] Scene 1: {P1_FILE.name} ({P1_FILE.stat().st_size} bytes)", flush=True)
                        browser.close()
                        return True

        browser.close()
        return False

if __name__ == "__main__":
    click_and_harvest()
