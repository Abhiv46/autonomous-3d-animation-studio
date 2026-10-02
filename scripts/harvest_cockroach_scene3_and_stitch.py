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
OUTPUT_DIR = BASE_DIR / "data" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

P1_FILE = RAW_CLIPS / "ep19_flying_cockroach_p1.mp4"
P2_FILE = RAW_CLIPS / "ep19_flying_cockroach_p2.mp4"
P3_OUT = RAW_CLIPS / "ep19_flying_cockroach_p3.mp4"
P3_SAMPLE = RAW_CLIPS / "ep19_flying_cockroach_p3_sample.png"
MASTER_FILE = OUTPUT_DIR / "ep19_flying_cockroach_master.mp4"

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

def stitch_master():
    print("[*] Stitching 3-scene master episode with FFmpeg...")
    concat_txt = BASE_DIR / "data" / "concat_temp_ep19.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for c in [P1_FILE, P2_FILE, P3_OUT]:
            f.write(f"file '{c.resolve()}'\n")

    cmd = [
        FFMPEG_BIN, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_txt),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        str(MASTER_FILE)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and MASTER_FILE.exists() and MASTER_FILE.stat().st_size > 1000000:
        print(f"[🏆 UPGRADED 3-SCENE MASTER SHORT STITCHED]: {MASTER_FILE.name} ({MASTER_FILE.stat().st_size} bytes)")
        return True
    print(f"[!] FFmpeg stitch failed: {res.stderr}")
    return False

def harvest_and_stitch():
    print("=" * 65)
    print("  WAITING FOR SCENE 3 RENDER & DOWNLOADING FROM TND")
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

        # Wait until render completes (stop button disappears)
        print("[*] Monitoring render completion...")
        for check in range(15):
            stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
            count = stop_btn.count()
            print(f"  Check {check+1}: Stop button count = {count}")
            if count == 0:
                print("[+] Render has finished!")
                break
            time.sleep(5)

        # If inside editor, go back to canvas
        back_btn = page.locator("button[aria-label*='back' i]").first
        if back_btn.count() > 0 and back_btn.is_visible():
            back_btn.click(force=True)
            page.wait_for_timeout(2000)

        # Newest video is Tile 0
        tiles = page.locator("flow-grid-tile-container, div.flow-grid-tile, [aria-label*='video' i]").all()
        print(f"[*] Found {len(tiles)} tiles on canvas. Tile 0 is Scene 3.")
        tiles[0].click(force=True)
        page.wait_for_timeout(2500)

        # Download button
        dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download'), [aria-label*='download' i]").first
        if dl_btn.count() > 0:
            print("[+] Found Download button, clicking...")
            dl_btn.click(force=True)
            page.wait_for_timeout(1500)

            target = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size'), button:has-text('1080p')").first
            if target.count() > 0:
                print(f"[+] Triggering download -> {P3_OUT.name}...")
                with page.expect_download(timeout=60000) as dl_info:
                    target.click(force=True)
                dl = dl_info.value
                dl.save_as(str(P3_OUT))
                page.wait_for_timeout(1000)

                if P3_OUT.exists() and P3_OUT.stat().st_size > 500000:
                    print(f"[🏆 DOWNLOAD COMPLETE]: {P3_OUT.name} ({P3_OUT.stat().st_size} bytes)")
                    extract_sample_frame(P3_OUT, P3_SAMPLE)
                    print(f"[🏆 SAMPLE FRAME EXTRACTED]: {P3_SAMPLE.name}")

        browser.close()

    # Now stitch the 3 scenes into the final master short
    if P3_OUT.exists():
        stitch_master()

if __name__ == "__main__":
    harvest_and_stitch()
