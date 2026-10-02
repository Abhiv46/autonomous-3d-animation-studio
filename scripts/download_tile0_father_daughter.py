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
OUT_VIDEO = RAW_CLIPS / "ep20_father_daughter_p1.mp4"
OUT_FRAME = RAW_CLIPS / "ep20_father_daughter_p1_sample.png"

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
FFMPEG_BIN = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

def download_tile0():
    print("=" * 65)
    print("  DOWNLOADING TILE 0 (FATHER AND DAUGHTER SCENE)")
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

        page.goto(PROJECT_URL, wait_until="domcontentloaded", timeout=40000)
        page.wait_for_timeout(4000)

        # Make sure canvas is shown
        back_btn = page.locator("button[aria-label*='back' i]").first
        if back_btn.count() > 0 and back_btn.is_visible():
            back_btn.click(force=True)
            page.wait_for_timeout(2000)

        tiles = page.locator("flow-grid-tile-container, div.flow-grid-tile, [aria-label*='video' i]").all()
        print(f"[*] Found {len(tiles)} tiles on canvas. Clicking Tile 0...")
        tiles[0].click(force=True)
        page.wait_for_timeout(2500)

        page.screenshot(path="data/ep20_tile0_opened.png")

        # Download button
        dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
        if dl_btn.count() > 0:
            print("[+] Found Download button, clicking...")
            dl_btn.click(force=True)
            page.wait_for_timeout(1500)

            target = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size'), button:has-text('1080p')").first
            if target.count() > 0:
                print(f"[+] Triggering download -> {OUT_VIDEO.name}...")
                with page.expect_download(timeout=60000) as dl_info:
                    target.click(force=True)
                dl = dl_info.value
                dl.save_as(str(OUT_VIDEO))
                page.wait_for_timeout(1000)

                if OUT_VIDEO.exists() and OUT_VIDEO.stat().st_size > 500000:
                    print(f"[🏆 DOWNLOAD COMPLETE]: {OUT_VIDEO.name} ({OUT_VIDEO.stat().st_size} bytes)")
                    subprocess.run([
                        FFMPEG_BIN, "-y",
                        "-ss", "00:00:03",
                        "-i", str(OUT_VIDEO),
                        "-vframes", "1",
                        "-q:v", "2",
                        str(OUT_FRAME)
                    ], capture_output=True)
                    print(f"[🏆 SAMPLE FRAME EXTRACTED]: {OUT_FRAME.name}")

        browser.close()

if __name__ == "__main__":
    download_tile0()
