import os
import sys
import time
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_URL = "https://flow.google.com/u/0/project/13f93410-698f-4e69-8e70-34c79b83ecb5"
BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
P1_OUT = RAW_CLIPS / "ep_15_fake_moustache_cop_p1.mp4"
P1_LAST = RAW_CLIPS / "ep_15_fake_moustache_cop_p1_last.png"

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
FFMPEG_BIN = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

def extract_last_frame(video_path, image_path):
    cmd = [
        FFMPEG_BIN, "-y",
        "-sseof", "-0.1",
        "-i", str(video_path),
        "-update", "1",
        "-q:v", "1",
        str(image_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0 and image_path.exists()

def download_and_extract():
    print(f"[*] Navigating to project {PROJECT_URL}...", flush=True)
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

        # Wait until stop button is gone (generation completed)
        for tick in range(12):
            stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
            print(f"[*] Tick {tick+1}: Stop button count = {stop_btn.count()}", flush=True)
            if stop_btn.count() == 0:
                print("[+] Stop button is gone — render is complete!", flush=True)
                break
            time.sleep(6)

        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\slot0_render_complete.png")

        # Click video card on canvas (left side)
        cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video, div.flow-grid-tile")
        print(f"[*] Found {cards.count()} video cards on canvas", flush=True)

        if cards.count() > 0:
            print("[+] Clicking video card...", flush=True)
            cards.first.click(force=True)
            page.wait_for_timeout(2500)

            # Look for Download button
            dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
            if dl_btn.count() > 0 and dl_btn.is_visible():
                print("[+] Clicking Download button...", flush=True)
                dl_btn.click(force=True)
                page.wait_for_timeout(1500)

                target_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size')").first
                if target_720.count() > 0:
                    print(f"[+] Clicking 720p download -> {P1_OUT.name}...", flush=True)
                    with page.expect_download(timeout=60000) as dl_info:
                        target_720.click(force=True)
                    dl = dl_info.value
                    dl.save_as(str(P1_OUT))
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(1000)

                    if P1_OUT.exists() and P1_OUT.stat().st_size > 1000000:
                        print(f"[🏆 SAVED] Scene 1: {P1_OUT.name} ({P1_OUT.stat().st_size} bytes)", flush=True)
                        last_ok = extract_last_frame(P1_OUT, P1_LAST)
                        if last_ok:
                            print(f"[🏆 FRAME ANCHOR EXTRACTED]: {P1_LAST.name} ({P1_LAST.stat().st_size} bytes)", flush=True)
                        browser.close()
                        return True

        browser.close()
        return False

if __name__ == "__main__":
    download_and_extract()
