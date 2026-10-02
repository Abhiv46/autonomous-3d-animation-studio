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

PROJECT_URL = "https://flow.google.com/u/0/project/1876f0f7-bc42-4764-86c9-35d76cb3a615"
BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
P1_OUT = RAW_CLIPS / "ep19_flying_cockroach_p1.mp4"
P1_SAMPLE = RAW_CLIPS / "ep19_flying_cockroach_p1_sample.png"

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
FFMPEG_BIN = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

def extract_sample_frame(video_path, image_path):
    cmd = [
        FFMPEG_BIN, "-y",
        "-ss", "00:00:03",
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "2",
        str(image_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0 and image_path.exists()

def download_cockroach_scene1():
    print("=" * 65)
    print("  DOWNLOADING SCENE 1 (THE FLYING COCKROACH STANDOFF) FROM TND")
    print("=" * 65)

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

        print(f"[*] Navigating to {PROJECT_URL}...")
        page.goto(PROJECT_URL, wait_until="domcontentloaded", timeout=40000)
        page.wait_for_timeout(4000)

        # Close any dialog or overlay by pressing Escape
        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)

        # The new video is the first video card on the canvas (top left)
        # Click on it to open in editor/preview
        first_tile = page.locator("flow-grid-tile-container, div.flow-grid-tile, [aria-label*='video' i]").first
        print("[*] Clicking the new video tile...")
        first_tile.click(force=True)
        page.wait_for_timeout(2500)

        page.screenshot(path="data/tnd_video_opened.png")

        # Click Download button in the header or player
        dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download'), [aria-label*='download' i]").first
        if dl_btn.count() > 0:
            print("[+] Found Download button, clicking...")
            dl_btn.click(force=True)
            page.wait_for_timeout(1500)

            # Select resolution (720p or Original)
            target = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size'), button:has-text('1080p')").first
            if target.count() > 0:
                print(f"[+] Triggering download -> {P1_OUT.name}...")
                with page.expect_download(timeout=60000) as dl_info:
                    target.click(force=True)
                dl = dl_info.value
                dl.save_as(str(P1_OUT))
                page.wait_for_timeout(1000)

                if P1_OUT.exists() and P1_OUT.stat().st_size > 500000:
                    print(f"[🏆 DOWNLOAD COMPLETE]: {P1_OUT.name} ({P1_OUT.stat().st_size} bytes)")
                    extract_sample_frame(P1_OUT, P1_SAMPLE)
                    print(f"[🏆 SAMPLE FRAME EXTRACTED]: {P1_SAMPLE.name}")

        browser.close()

if __name__ == "__main__":
    download_cockroach_scene1()
