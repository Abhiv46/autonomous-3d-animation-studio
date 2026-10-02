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

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
OUTPUT_DIR = BASE_DIR / "data" / "output"

P1_FILE = RAW_CLIPS / "ep_15_fake_moustache_cop_p1.mp4"
P2_FILE = RAW_CLIPS / "ep_15_fake_moustache_cop_p2.mp4"
P3_FILE = RAW_CLIPS / "ep_15_fake_moustache_cop_p3.mp4"
MASTER_FILE = OUTPUT_DIR / "ep_15_fake_moustache_cop_master.mp4"

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
FFMPEG_BIN = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

PROJECT_URL = "https://flow.google.com/u/1/project/28704e19-7200-4c0b-ab84-8e072ef4e201"

def inspect_and_download():
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
        page.screenshot(path=str(BASE_DIR / "data" / "slot1_p3_canvas.png"))

        cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video")
        count = cards.count()
        print(f"[*] Found {count} video elements on canvas.", flush=True)

        # In Google Flow grid, the newest generation is often the first card in the grid!
        # Let's inspect the cards:
        downloaded = False
        for idx in range(count):
            print(f"[*] Trying card index {idx}...", flush=True)
            cards.nth(idx).click(force=True)
            page.wait_for_timeout(2500)
            dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
            if dl_btn.count() > 0 and dl_btn.is_visible():
                dl_btn.click(force=True)
                page.wait_for_timeout(1500)
                target_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size')").first
                if target_720.count() > 0:
                    temp_p3 = RAW_CLIPS / f"temp_card_{idx}.mp4"
                    print(f"[+] Downloading card {idx} -> {temp_p3.name}...", flush=True)
                    with page.expect_download(timeout=60000) as dl_info:
                        target_720.click(force=True)
                    dl = dl_info.value
                    dl.save_as(str(temp_p3))
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(1000)

                    # Check if this clip is different from p2 (compare sizes or duration)
                    if temp_p3.exists():
                        print(f"[✓ Saved]: {temp_p3.name} ({temp_p3.stat().st_size} bytes)", flush=True)
                        if abs(temp_p3.stat().st_size - P2_FILE.stat().st_size) > 50000:
                            # Different size than p2, so this is p3!
                            temp_p3.replace(P3_FILE)
                            print(f"[🏆 IDENTIFIED AS SCENE 3]: {P3_FILE.name} ({P3_FILE.stat().st_size} bytes)", flush=True)
                            downloaded = True
                            break
                        else:
                            # Same size as p2, might be p2 or similar
                            print(f"[*] Card {idx} size matches p2 closely.", flush=True)

        if not downloaded:
            # If still not downloaded, take the first temp card if any
            for idx in range(count):
                temp_p3 = RAW_CLIPS / f"temp_card_{idx}.mp4"
                if temp_p3.exists() and temp_p3.stat().st_size > 1000000:
                    temp_p3.replace(P3_FILE)
                    print(f"[✓ Adopted as P3]: {P3_FILE.name}", flush=True)
                    downloaded = True
                    break

        browser.close()
        return downloaded

def stitch_master():
    concat_txt = BASE_DIR / "data" / "concat_temp_ep15.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for c in [P1_FILE, P2_FILE, P3_FILE]:
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
        print(f"[🏆 MASTER SHORT STITCHED]: {MASTER_FILE.name} ({MASTER_FILE.stat().st_size} bytes)", flush=True)
        return True
    print(f"[!] FFmpeg stitch failed: {res.stderr}", flush=True)
    return False

def main():
    ok = inspect_and_download()
    if ok and P3_FILE.exists():
        stitch_ok = stitch_master()
        if stitch_ok:
            print("\n" + "=" * 60, flush=True)
            print("  DUAL-PLATFORM AUTO-PUBLISHING TO YOUTUBE & TIKTOK", flush=True)
            print("=" * 60, flush=True)
            try:
                from dual_publisher_ep15 import main as publish_all
                publish_all()
            except Exception as e:
                print(f"[!] Publisher exception: {e}", flush=True)

if __name__ == "__main__":
    main()
