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
P2_FILE = RAW_CLIPS / "ep_15_scene2_slot0_clean.mp4"
P3_REAL = RAW_CLIPS / "ep_15_scene3_real.mp4"
P3_SAMPLE = RAW_CLIPS / "ep_15_scene3_real_sample.png"
MASTER_FILE = OUTPUT_DIR / "ep_15_fake_moustache_cop_master.mp4"

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
FFMPEG_BIN = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

PROJECT_URL = "https://flow.google.com/u/0/project/17d9a600-d978-4f15-a549-e6a4b271e629"

def stitch_master():
    concat_txt = BASE_DIR / "data" / "concat_temp_ep15_v3.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for c in [P1_FILE, P2_FILE, P3_REAL]:
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
        print(f"[🏆 UPGRADED 3-SCENE MASTER SHORT STITCHED]: {MASTER_FILE.name} ({MASTER_FILE.stat().st_size} bytes)", flush=True)
        return True
    print(f"[!] FFmpeg stitch failed: {res.stderr}", flush=True)
    return False

def run():
    print("=" * 65, flush=True)
    print("  APPROVING & HARVESTING REAL SCENE 3 ON PLUS SLOT 0", flush=True)
    print("=" * 65, flush=True)

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

        # Click Approve option
        print("[*] Looking for Approve option...", flush=True)
        opt = page.locator("div:has-text('Approve'), span:has-text('Approve'), button:has-text('Approve')")
        clicked = False
        for idx in range(opt.count()):
            el = opt.nth(idx)
            if el.is_visible() and ("Approve" in el.inner_text()):
                print(f"[+] Clicking option: {el.inner_text().strip()[:20]}", flush=True)
                el.click(force=True)
                clicked = True
                break

        if not clicked:
            print("[+] Clicking coordinate (900, 755)...", flush=True)
            page.mouse.click(900, 755)

        page.wait_for_timeout(3000)
        page.screenshot(path=str(BASE_DIR / "data" / "debug_s3_approval_clicked.png"))

        # Monitor render until 2 video cards exist
        print("[*] Monitoring render progress (waiting for 2nd video card)...", flush=True)
        start_t = time.time()
        second_card_ready = False

        for tick in range(30):
            cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video")
            count = cards.count()
            has_stop = page.locator("button:has-text('Stop')").count() > 0
            print(f"[*] Tick {tick*5}s: Found {count} cards. Stop button visible: {has_stop}", flush=True)
            if count >= 2:
                second_card_ready = True
                print(f"[+] Second card detected! Render complete after {int(time.time() - start_t)}s!", flush=True)
                break
            time.sleep(5)

        page.screenshot(path=str(BASE_DIR / "data" / "debug_s3_rendered_cards.png"))

        cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video")
        if cards.count() >= 2:
            # First card in the grid is usually the newest generation
            newest_card = cards.first
            print("[+] Clicking newest card...", flush=True)
            newest_card.click(force=True)
            page.wait_for_timeout(2500)

            dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
            if dl_btn.count() > 0 and dl_btn.is_visible():
                dl_btn.click(force=True)
                page.wait_for_timeout(1500)
                target_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size')").first
                if target_720.count() > 0:
                    print(f"[+] Downloading Scene 3 720p -> {P3_REAL.name}...", flush=True)
                    with page.expect_download(timeout=60000) as dl_info:
                        target_720.click(force=True)
                    dl = dl_info.value
                    dl.save_as(str(P3_REAL))
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(1000)

                    if P3_REAL.exists() and P3_REAL.stat().st_size > 1000000:
                        print(f"[🏆 REAL SCENE 3 SAVED]: {P3_REAL.name} ({P3_REAL.stat().st_size} bytes)", flush=True)
                        subprocess.run([FFMPEG_BIN, "-y", "-ss", "00:00:03", "-i", str(P3_REAL), "-vframes", "1", str(P3_SAMPLE)], capture_output=True)
                        print(f"[📸 Sample Frame Extracted]: {P3_SAMPLE.name}", flush=True)

        browser.close()

    if P3_REAL.exists() and P3_REAL.stat().st_size > 1000000:
        stitch_ok = stitch_master()
        if stitch_ok:
            print("\n" + "=" * 60, flush=True)
            print("  RE-PUBLISHING MASTER SHORT TO YOUTUBE & TIKTOK", flush=True)
            print("=" * 60, flush=True)
            try:
                from dual_publisher_ep15 import main as publish_all
                publish_all()
            except Exception as e:
                print(f"[!] Publisher exception: {e}", flush=True)

if __name__ == "__main__":
    run()
