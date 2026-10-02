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
OUTPUT_DIR = BASE_DIR / "data" / "output"

P1_FILE = RAW_CLIPS / "ep_15_fake_moustache_cop_p1.mp4"
P1_LAST = RAW_CLIPS / "ep_15_fake_moustache_cop_p1_last.png"

P2_FILE = RAW_CLIPS / "ep_15_fake_moustache_cop_p2.mp4"
P2_LAST = RAW_CLIPS / "ep_15_fake_moustache_cop_p2_last.png"

P3_FILE = RAW_CLIPS / "ep_15_fake_moustache_cop_p3.mp4"
P3_LAST = RAW_CLIPS / "ep_15_fake_moustache_cop_p3_last.png"

MASTER_FILE = OUTPUT_DIR / "ep_15_fake_moustache_cop_master.mp4"

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
FFMPEG_BIN = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

P2_PROMPT = (
    "High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. "
    "Full 3D CGI animation. CONTINUITY: Continues directly from attached image. "
    "Kaartik in yellow polo with drawn black moustache and Kaavya with wooden spatula in modern kitchen. "
    "Kaartik slams his tiny hand playfully on the clean kitchen counter and inspects the glass biscuit jar through his red magnifying glass. "
    "3D Indian mother Pinki (25 years old, powder-blue kurti) drops a kitchen towel in comical theatrical surrender, "
    "raising both hands with exaggerated wide eyes: 'Arre Inspector Sahab, hum nirdosh hain!' "
    "Kaavya blows through a straw making funny siren noises. "
    "Vibrant Pixar 3D lighting, crisp CGI render, rich subsurface scattering. "
    "STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays."
)

P3_PROMPT = (
    "High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. "
    "Full 3D CGI animation. CONTINUITY: Continues directly from attached image in kitchen. "
    "Mummy Pinki hands Kaartik and Kaavya huge warm chocolate chip cookies. "
    "Kaartik takes a huge bite; as he rubs his mouth with chubby hand, the black drawn moustache smudges across his cheeks into funny cat whiskers! "
    "Kaavya giggles hysterically, clapping with cookie crumbs on her nose. "
    "Mummy pulls both kids into a warm laughing hug. Kaartik winks at the camera with chocolate smile. "
    "Vibrant Pixar 3D lighting, crisp CGI render. "
    "STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays."
)

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

def attach_anchor_frame(page, image_path):
    print(f"[*] Attaching Frame Anchor: {image_path.name}...", flush=True)
    add_menu = page.locator("[aria-label*='Add media menu' i], [aria-label*='Add ingredients' i], button:has-text('add')").first
    if add_menu.count() > 0:
        add_menu.click(force=True)
        page.wait_for_timeout(1000)

        with page.expect_file_chooser() as fc_info:
            upload_item = page.locator("button:has-text('Upload'), [role='menuitem']:has-text('Upload')").first
            upload_item.click(force=True)

        fc = fc_info.value
        fc.set_files(str(image_path))
        print(f"[*] File set in chooser: {image_path.name}. Waiting 5s...", flush=True)
        page.wait_for_timeout(5000)

        add_to_prompt = page.locator("button:has-text('Add to prompt'), [role='button']:has-text('Add to prompt')").first
        if add_to_prompt.count() > 0 and add_to_prompt.is_visible():
            add_to_prompt.click(force=True)
            page.wait_for_timeout(1500)
            page.keyboard.press("Escape")
            page.wait_for_timeout(1000)

        print(f"[✓ Anchor Attached]: {image_path.name}", flush=True)
        return True
    return False

def generate_part(page, prompt_text, out_file, last_frame_file, anchor_image=None):
    editor = page.locator("div.ProseMirror").first
    editor.click(force=True)
    page.wait_for_timeout(300)
    editor.fill(prompt_text)
    page.wait_for_timeout(1000)
    print("[+] Prompt text filled into editor.", flush=True)

    if anchor_image and anchor_image.exists():
        attach_anchor_frame(page, anchor_image)

    page.screenshot(path=str(BASE_DIR / f"data/debug_{out_file.stem}_ready.png"))

    start_btn = page.locator("button[aria-label*='Start generation' i]").first
    if start_btn.count() > 0:
        start_btn.click(force=True)
    else:
        page.keyboard.press("Enter")

    print("[*] Prompt submitted, waiting for approval dialog...", flush=True)
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

    page.screenshot(path=str(BASE_DIR / f"data/debug_{out_file.stem}_after_submit.png"))

    print("[*] Waiting for video render (~70-90s)...", flush=True)
    time.sleep(60)

    for _ in range(16):
        stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
        if stop_btn.count() == 0:
            print("[+] Render finished or no stop button detected!", flush=True)
            break
        time.sleep(5)

    page.screenshot(path=str(BASE_DIR / f"data/debug_{out_file.stem}_after_render.png"))

    # Download 720p
    cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video")
    if cards.count() > 0:
        print(f"[+] Found {cards.count()} video elements. Clicking latest...", flush=True)
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
                    extract_last_frame(out_file, last_frame_file)
                    return True
    return False

def stitch_master(clips, output_path):
    concat_txt = BASE_DIR / "data" / "concat_temp_ep15.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for c in clips:
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
        str(output_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000000

def run_pipeline():
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
            print("[*] Project canvas not loaded directly. Checking https://flow.google.com/u/0/ ...", flush=True)
            page.goto("https://flow.google.com/u/0/", wait_until="domcontentloaded")
            page.wait_for_timeout(4000)
            proj_card = page.locator("flow-project-card, [role='listitem'], div[class*='project']").first
            if proj_card.count() > 0:
                print("[+] Clicking recent project card...", flush=True)
                proj_card.click(force=True)
                page.wait_for_timeout(5000)
            else:
                new_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i]").first
                if new_btn.count() > 0:
                    print("[+] Creating new project...", flush=True)
                    new_btn.click(force=True)
                    page.wait_for_timeout(5000)

        print(f"[*] Ready on Canvas URL: {page.url}", flush=True)

        # Scene 2
        print("\n" + "=" * 60, flush=True)
        print("  PRODUCING SCENE 2 WITH LAST-FRAME ANCHOR", flush=True)
        print("=" * 60, flush=True)
        s2_ok = generate_part(page, P2_PROMPT, P2_FILE, P2_LAST, anchor_image=P1_LAST)

        if not s2_ok:
            print("[!] Scene 2 failed.", flush=True)
            browser.close()
            return

        # Scene 3
        print("\n" + "=" * 60, flush=True)
        print("  PRODUCING SCENE 3 WITH LAST-FRAME ANCHOR", flush=True)
        print("=" * 60, flush=True)
        s3_ok = generate_part(page, P3_PROMPT, P3_FILE, P3_LAST, anchor_image=P2_LAST)

        browser.close()

        if s3_ok:
            print("\n" + "=" * 60, flush=True)
            print("  STITCHING MASTER SHORT (FFmpeg High-Definition)", flush=True)
            print("=" * 60, flush=True)
            stitch_ok = stitch_master([P1_FILE, P2_FILE, P3_FILE], MASTER_FILE)
            if stitch_ok:
                print(f"[🎉 MASTER CREATED]: {MASTER_FILE.name} ({MASTER_FILE.stat().st_size} bytes)", flush=True)

if __name__ == "__main__":
    run_pipeline()
