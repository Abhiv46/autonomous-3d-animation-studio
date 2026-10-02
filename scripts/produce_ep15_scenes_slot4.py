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

SLOT_URL = "https://flow.google.com/u/4/"

P2_PROMPT = (
    "High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. "
    "Full 3D CGI animation. Bright sunlit modern kitchen of Indian home. "
    "Chubby toddler boy Kaartik (5 years old, bright yellow polo shirt, drawn black handlebar moustache on cheeks) "
    "playfully slams his small hand onto the clean kitchen counter, pointing his red magnifying glass at the high shelf cookie jar. "
    "Beside him, cute toddler sister Kaavya (3.5 years old, pink frock, double buns) blows through a straw making funny siren noises. "
    "Indian mother Pinki (25 years old, powder-blue kurti) drops her dish towel in dramatic theatrical surrender, "
    "raising both hands with wide playful eyes: 'Arre Inspector Sahab, hum nirdosh hain!' "
    "Vibrant Pixar 3D lighting, crisp CGI render, rich subsurface scattering. "
    "STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays."
)

P3_PROMPT = (
    "High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. "
    "Full 3D CGI animation. Bright sunlit modern kitchen of Indian home. "
    "Indian mother Pinki (25 years old, powder-blue kurti) smiles warmly and hands two giant fresh chocolate chip cookies to "
    "chubby toddler boy Kaartik (5 years old, bright yellow polo shirt) and cute toddler sister Kaavya (pink frock, double buns). "
    "Kaartik takes a huge happy bite; as he rubs his mouth with chubby hand, the black drawn moustache smudges across his cheeks into funny cat whiskers! "
    "Kaavya giggles hysterically, clapping with cookie crumbs on her nose. "
    "Vibrant Pixar 3D lighting, crisp CGI render. "
    "STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays."
)

def generate_video(page, prompt_text, out_file):
    print(f"\n[*] Generating: {out_file.name}...", flush=True)
    editor = page.locator("div.ProseMirror").first
    if editor.count() == 0:
        print("[-] Editor not found!", flush=True)
        return False

    editor.click(force=True)
    page.wait_for_timeout(300)
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    editor.fill(prompt_text)
    page.wait_for_timeout(1000)

    start_btn = page.locator("button[aria-label*='Start generation' i]").first
    if start_btn.count() > 0:
        start_btn.click(force=True)
    else:
        page.keyboard.press("Enter")

    print("[*] Prompt submitted, checking for approval...", flush=True)
    for _ in range(20):
        opt = page.locator("div.option-row:has-text('Always approve'), span.option-label:has-text('Always approve'), div.option-row:has-text('Approve'), button:has-text('Always approve')").first
        if opt.count() > 0 and opt.is_visible():
            box = opt.bounding_box()
            if box:
                page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
            else:
                opt.click(force=True)
            print("[+] Clicked Approval!", flush=True)
            break
        time.sleep(2)

    print("[*] Waiting for video render (~70-90s)...", flush=True)
    time.sleep(60)

    for _ in range(16):
        stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
        if stop_btn.count() == 0:
            print("[+] Render finished!", flush=True)
            break
        time.sleep(5)

    # Download 720p
    cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video")
    if cards.count() > 0:
        # Click the most recent card (first or last depending on DOM, try last/first)
        cards.first.click(force=True)
        page.wait_for_timeout(2500)
        dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
        if dl_btn.count() > 0 and dl_btn.is_visible():
            dl_btn.click(force=True)
            page.wait_for_timeout(1500)
            target_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size')").first
            if target_720.count() > 0:
                print(f"[+] Downloading 720p -> {out_file.name}...", flush=True)
                with page.expect_download(timeout=60000) as dl_info:
                    target_720.click(force=True)
                dl = dl_info.value
                dl.save_as(str(out_file))
                page.keyboard.press("Escape")
                page.wait_for_timeout(1000)

                if out_file.exists() and out_file.stat().st_size > 1000000:
                    print(f"[🏆 SAVED]: {out_file.name} ({out_file.stat().st_size} bytes)", flush=True)
                    return True
    return False

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
    print("=" * 65, flush=True)
    print("  PRODUCING EPISODE 15 SCENES 2 & 3 ON SLOT 4 (infolillylooks@gmail.com)", flush=True)
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

        print(f"[*] Navigating to Slot 4: {SLOT_URL}...", flush=True)
        page.goto(SLOT_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        new_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i], div:has-text('New project')").first
        if new_btn.count() > 0 and new_btn.is_visible():
            print("[+] Clicking New project...", flush=True)
            new_btn.click(force=True)
            page.wait_for_timeout(5000)

        print(f"[*] Project Canvas URL: {page.url}", flush=True)

        # Generate Scene 2
        s2_ok = generate_video(page, P2_PROMPT, P2_FILE)
        if not s2_ok:
            print("[!] Scene 2 generation failed.", flush=True)
            browser.close()
            return

        # Generate Scene 3
        s3_ok = generate_video(page, P3_PROMPT, P3_FILE)
        if not s3_ok:
            print("[!] Scene 3 generation failed.", flush=True)
            browser.close()
            return

        browser.close()

    if s2_ok and s3_ok:
        master_ok = stitch_master()
        if master_ok:
            print("[*] Master short ready! Launching dual publisher...", flush=True)
            from dual_publisher_ep15 import main as publish_all
            publish_all()

if __name__ == "__main__":
    main()
