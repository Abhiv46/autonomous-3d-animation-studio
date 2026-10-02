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

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
OUTPUT_DIR = BASE_DIR / "data" / "output"
FFMPEG_BIN = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

SLOT = 7
EMAIL = "rkumar.ukb@gmail.com"
SCENE_PROMPT = (
    "CoComelon and Pixar 3D animated style, 9:16 vertical orientation, 8 seconds. "
    "Full 3D CGI animation. Modern warm vibrant Indian living room. Adorable chubby 3D toddler boy Kaartik "
    "(5 years old, rounded cute cheeks, big expressive glassy 3D brown eyes, volumetric 3D black hair, bright yellow polo shirt, blue shorts) "
    "gleefully points a colorful toy video game remote controller at his beautiful 3D mother Pinki (25 years old, smooth 3D features, powder-blue Indian kurti). "
    "Cute 3D toddler sister Kaavya (3 years old, chubby cheeks, curly hair, bright pink frock) giggles excitedly. "
    "Smooth fluid 3D character motion, soft volumetric studio lighting, rich 3D subsurface scattering, high-end Pixar Disney render. "
    "STRICTLY NO 2D drawings, NO flat sketches, NO comic book outlines, NO speech bubbles, NO text."
)
OUT_FILE = RAW_CLIPS / "ep18_3d_p1.mp4"

def generate_and_download_scene1():
    print("=" * 60, flush=True)
    print(f"  GENERATING SCENE 1 ON SLOT {SLOT} ({EMAIL})", flush=True)
    print("=" * 60, flush=True)

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            accept_downloads=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = ctx.new_page()
        url = f"https://flow.google.com/u/{SLOT}/"
        print(f"[*] Navigating to {url}...", flush=True)
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(3000)

        # Click "+ New project"
        new_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i]").first
        if new_btn.count() > 0 and new_btn.is_visible():
            new_btn.click()
            page.wait_for_timeout(4000)

        print(f"[+] Canvas ready: {page.url}", flush=True)

        # Configure settings to 9:16
        tune_btn = page.locator("button:has-text('tune'), [aria-label*='settings' i], [aria-label*='tune' i]").last
        if tune_btn.count() > 0 and tune_btn.is_visible():
            try:
                tune_btn.click()
                page.wait_for_timeout(1000)
                never_radio = page.locator("span:has-text('Never'), [role='radio']:has-text('Never'), div:has-text('Never')").last
                if never_radio.count() > 0:
                    never_radio.click(force=True)
                    page.wait_for_timeout(300)
                v_916 = page.locator("button:has-text('9:16'), [role='button']:has-text('9:16'), div:has-text('9:16')").last
                if v_916.count() > 0:
                    v_916.click(force=True)
                    page.wait_for_timeout(300)
                save_btn = page.locator("button:has-text('Save'), [role='button']:has-text('Save')").first
                if save_btn.count() > 0 and save_btn.is_visible():
                    save_btn.click()
                    page.wait_for_timeout(1000)
            except Exception as e:
                print(f"[!] Tune config warning: {e}", flush=True)

        # Enter Prompt
        print(f"[*] Submitting Scene 1 prompt...", flush=True)
        editor = page.locator("[contenteditable='true'], div.ProseMirror, textarea").first
        if editor.count() > 0:
            editor.click()
            page.wait_for_timeout(300)
            editor.fill(SCENE_PROMPT)
            page.wait_for_timeout(500)
            send_btn = page.locator("button:has-text('arrow_forward'), button[aria-label*='Submit' i], button.send-button").first
            if send_btn.count() > 0 and send_btn.is_visible():
                send_btn.click()
            else:
                page.keyboard.press("Enter")
            print(f"[🚀 SENT] Scene 1 prompt dispatched!", flush=True)

        # Check approvals
        for _ in range(8):
            time.sleep(1)
            target = page.locator("button:has-text('Always approve'), [role='button']:has-text('Always approve'), div:has-text('Always approve')")
            if target.count() > 0 and target.last.is_visible():
                print(f"[✓] Auto-approving credits...", flush=True)
                target.last.click(force=True)
                page.wait_for_timeout(1000)
                break
            app_target = page.locator("button:has-text('Approve'), [role='button']:has-text('Approve')")
            if app_target.count() > 0 and app_target.last.is_visible():
                print(f"[✓] Approving credits...", flush=True)
                app_target.last.click(force=True)
                page.wait_for_timeout(1000)
                break

        # Wait for render (~75s)
        print("[*] Waiting for Veo render (~75s)...", flush=True)
        start_time = time.time()
        for i in range(1, 20):
            time.sleep(5)
            elapsed = int(time.time() - start_time)
            stop_btn = page.locator("button:has-text('Stop'), button[aria-label='Stop']")
            is_rendering = stop_btn.count() > 0 and stop_btn.first.is_visible()
            vids = page.locator("video, [aria-label*='Open video in editor' i]").count()
            print(f"[{elapsed}s] Slot {SLOT}: {'Render' if is_rendering else 'Ready'} ({vids} vids)", flush=True)
            if not is_rendering and vids > 0 and elapsed >= 30:
                print(f"[+] Render ready after {elapsed}s!", flush=True)
                break

        # Download clip
        print("[*] Attempting download for Scene 1...", flush=True)
        cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video")
        download_success = False
        if cards.count() > 0:
            cards.last.click(force=True)
            page.wait_for_timeout(2500)
            
            dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
            if dl_btn.count() > 0 and dl_btn.is_visible():
                dl_btn.click(force=True)
                page.wait_for_timeout(1500)
                
                target_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size')").first
                if target_720.count() > 0:
                    print(f"[+] Triggering 720p download -> {OUT_FILE}...", flush=True)
                    with page.expect_download(timeout=60000) as dl_info:
                        target_720.click(force=True)
                    dl = dl_info.value
                    dl.save_as(str(OUT_FILE))
                    print(f"[🏆] SAVED: {OUT_FILE.name} ({OUT_FILE.stat().st_size} bytes)", flush=True)
                    download_success = True

        if not download_success:
            page.screenshot(path=str(BASE_DIR / "data" / "slot7_error.png"))
            print("[!] Download failed on Slot 7", flush=True)

        ctx.close()
        return download_success

def stitch_masterpiece():
    p1 = RAW_CLIPS / "ep18_3d_p1.mp4"
    p2 = RAW_CLIPS / "ep18_3d_p2.mp4"
    p3 = RAW_CLIPS / "ep18_3d_p3.mp4"

    if not (p1.exists() and p2.exists() and p3.exists()):
        print(f"[!] Missing parts: p1={p1.exists()}, p2={p2.exists()}, p3={p3.exists()}", flush=True)
        return False

    final_output = OUTPUT_DIR / "ep_18_magic_freeze_remote_final.mp4"
    concat_list = BASE_DIR / "data" / "concat_3d_ep18.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        f.write(f"file '{p1.resolve()}'\n")
        f.write(f"file '{p2.resolve()}'\n")
        f.write(f"file '{p3.resolve()}'\n")

    cmd = [
        FFMPEG_BIN, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        str(final_output)
    ]

    print(f"[*] Stitching with FFmpeg...", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and final_output.exists() and final_output.stat().st_size > 0:
        print(f"[🎉 MASTERPIECE READY] {final_output.name} ({final_output.stat().st_size / (1024*1024):.2f} MB)", flush=True)
        verify_frame = BASE_DIR / "data" / "ep18_cocomelon_test_frame.png"
        subprocess.run([FFMPEG_BIN, "-y", "-ss", "00:00:04", "-i", str(final_output), "-vframes", "1", str(verify_frame)], capture_output=True)
        print(f"[📸 Verification Frame Saved]: {verify_frame}", flush=True)
        return True
    else:
        print(f"[!] Stitch failed: {res.stderr}", flush=True)
        return False

if __name__ == "__main__":
    if generate_and_download_scene1():
        stitch_masterpiece()
