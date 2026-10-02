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
P3_FILE = RAW_CLIPS / "ep_15_scene3_slot0_clean.mp4"
P3_SAMPLE = RAW_CLIPS / "ep_15_scene3_slot0_clean_sample.png"
MASTER_FILE = OUTPUT_DIR / "ep_15_fake_moustache_cop_master.mp4"

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
FFMPEG_BIN = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

PROJECT_URL = "https://flow.google.com/u/0/project/17d9a600-d978-4f15-a549-e6a4b271e629"

SCENE_3_PROMPT = (
    "High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. "
    "Full 3D CGI animation. Bright sunlit modern kitchen of Indian home. "
    "Toddler eye-level close-up comedy climax. "
    "Chubby 3D toddler boy Kaartik (5 years old, bright yellow polo shirt, round blushing cheeks, dark messy toddler hair fringe) "
    "happily holds a giant warm chocolate chip cookie in both chubby hands, taking a huge delicious bite with puffed cheeks. "
    "As he wipes his chocolate-smeared mouth with the back of his chubby hand, the drawn black moustache smudges across his face "
    "into funny messy cat whiskers! "
    "Beside him, cute toddler sister Kaavya (3.5 years old, bright pink dress, double hair buns with pink ties) "
    "bursts into adorable giggles, pointing and clapping with pure joy. "
    "Kaartik looks directly at the camera with a big chocolatey grin and winks playfully. "
    "Vibrant Pixar 3D lighting, crisp CGI render, rich subsurface skin scattering, fluid cartoon character animation. "
    "STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays."
)

def stitch_master():
    concat_txt = BASE_DIR / "data" / "concat_temp_ep15_v2.txt"
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
        print(f"[🏆 UPGRADED MASTER SHORT STITCHED]: {MASTER_FILE.name} ({MASTER_FILE.stat().st_size} bytes)", flush=True)
        return True
    print(f"[!] FFmpeg stitch failed: {res.stderr}", flush=True)
    return False

def run():
    print("=" * 65, flush=True)
    print("  GENERATING SCENE 3 ON PLUS SLOT 0 (TecHWirE9999@gmail.com)", flush=True)
    print(f"  Canvas URL: {PROJECT_URL}", flush=True)
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

        editor = page.locator("div.ProseMirror").first
        if editor.count() == 0:
            print("[-] Editor not found!", flush=True)
            browser.close()
            return

        editor.click(force=True)
        page.wait_for_timeout(300)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        editor.fill(SCENE_3_PROMPT)
        page.wait_for_timeout(1000)

        start_btn = page.locator("button[aria-label*='Start generation' i]").first
        if start_btn.count() > 0:
            start_btn.click(force=True)
        else:
            page.keyboard.press("Enter")

        print("[*] Prompt submitted. Checking approval...", flush=True)
        for _ in range(20):
            opt = page.locator("div.option-row:has-text('Always approve'), span.option-label:has-text('Always approve'), div.option-row:has-text('Approve'), button:has-text('Always approve'), button:has-text('Approve')").first
            if opt.count() > 0 and opt.is_visible():
                box = opt.bounding_box()
                if box:
                    page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                else:
                    opt.click(force=True)
                print("[+] Clicked Approval for Scene 3!", flush=True)
                break
            time.sleep(2)

        page.screenshot(path=str(BASE_DIR / "data" / "debug_slot0_s3_submitted.png"))

        print("[*] Waiting for Scene 3 render (~70-90s)...", flush=True)
        time.sleep(60)

        for _ in range(16):
            stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
            if stop_btn.count() == 0:
                print("[+] Scene 3 render finished!", flush=True)
                break
            time.sleep(5)

        page.screenshot(path=str(BASE_DIR / "data" / "debug_slot0_s3_rendered.png"))

        # Download newest video card (first card in grid)
        cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video")
        if cards.count() > 0:
            print(f"[+] Found {cards.count()} video elements. Clicking newest...", flush=True)
            cards.first.click(force=True)
            page.wait_for_timeout(2500)
            dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
            if dl_btn.count() > 0 and dl_btn.is_visible():
                dl_btn.click(force=True)
                page.wait_for_timeout(1500)
                target_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size')").first
                if target_720.count() > 0:
                    print(f"[+] Downloading 720p to {P3_FILE.name}...", flush=True)
                    with page.expect_download(timeout=60000) as dl_info:
                        target_720.click(force=True)
                    dl = dl_info.value
                    dl.save_as(str(P3_FILE))
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(1000)

                    if P3_FILE.exists() and P3_FILE.stat().st_size > 1000000:
                        print(f"[🏆 SAVED]: {P3_FILE.name} ({P3_FILE.stat().st_size} bytes)", flush=True)
                        subprocess.run([FFMPEG_BIN, "-y", "-ss", "00:00:03", "-i", str(P3_FILE), "-vframes", "1", str(P3_SAMPLE)], capture_output=True)
                        print(f"[📸 Sample Frame Extracted]: {P3_SAMPLE.name}", flush=True)

        browser.close()

    if P3_FILE.exists() and P3_FILE.stat().st_size > 1000000:
        stitch_ok = stitch_master()
        if stitch_ok:
            print("\n" + "=" * 60, flush=True)
            print("  RE-PUBLISHING UPGRADED MASTER TO YOUTUBE & TIKTOK", flush=True)
            print("=" * 60, flush=True)
            try:
                from dual_publisher_ep15 import main as publish_all
                publish_all()
            except Exception as e:
                print(f"[!] Publisher exception: {e}", flush=True)

if __name__ == "__main__":
    run()
