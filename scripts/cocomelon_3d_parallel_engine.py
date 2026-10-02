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
RAW_CLIPS.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

# Benchmark CoComelon & Pixar 3D CGI Scenes for Episode 18
EPISODE_ID = "ep_18_magic_freeze_remote"
SCENES = [
    {
        "part": 1,
        "slot": 2,
        "email": "rkumar.pub@gmail.com",
        "label": "Part 1 - The Magic Remote Playful Freeze",
        "prompt": (
            "CoComelon and Pixar 3D animated style, 9:16 vertical orientation, 8 seconds. "
            "Full 3D CGI animation. Modern warm vibrant Indian living room. Adorable chubby 3D toddler boy Kaartik "
            "(5 years old, rounded cute cheeks, big expressive glassy 3D brown eyes, volumetric 3D black hair, bright yellow polo shirt, blue shorts) "
            "gleefully points a colorful toy video game remote controller at his beautiful 3D mother Pinki (25 years old, smooth 3D features, powder-blue Indian kurti). "
            "Cute 3D toddler sister Kaavya (3 years old, chubby cheeks, curly hair, bright pink frock) giggles excitedly. "
            "Smooth fluid 3D character motion, soft volumetric studio lighting, rich 3D subsurface scattering, high-end Pixar Disney render. "
            "STRICTLY NO 2D drawings, NO flat sketches, NO comic book outlines, NO speech bubbles, NO text."
        ),
        "outfile": RAW_CLIPS / "ep18_3d_p1.mp4"
    },
    {
        "part": 2,
        "slot": 5,
        "email": "elegantdriveways4u@gmail.com",
        "label": "Part 2 - Mummy Hilariously Freezes Like a Toy Statue",
        "prompt": (
            "CoComelon and Pixar 3D animated style, 9:16 vertical orientation, 8 seconds. "
            "Full 3D CGI animation. Modern vibrant Indian living room. The 3D mother Pinki (powder-blue kurti) hilariously freezes "
            "completely still like a funny toy statue mid-step holding a basket of soft folded towels, eyes playfully wide open in frozen comic shock! "
            "Chubby 3D toddler Kaartik (yellow polo) tiptoes around the frozen statue examining her with mischievous wide 3D smiles. "
            "Rich Pixar 3D CGI lighting, glossy realistic 3D hair and skin shaders, volumetric depth of field, adorable CoComelon 3D toddler proportions. "
            "STRICTLY NO 2D cartoon, NO flat art, NO comic speech bubbles, NO written words."
        ),
        "outfile": RAW_CLIPS / "ep18_3d_p2.mp4"
    },
    {
        "part": 3,
        "slot": 6,
        "email": "abhiv446@gmail.com",
        "label": "Part 3 - Tickle Climax & Warm Family Cuddle",
        "prompt": (
            "CoComelon and Pixar 3D animated style, 9:16 vertical orientation, 8 seconds. "
            "Full 3D CGI animation. Sunlit modern Indian living room. Adorable 3D toddler Kaavya (bright pink frock) runs over excitedly "
            "and tickles frozen Mummy's waist! Pinki unfreezes, bursting into joyful laughter and playfully dropping soft pillows, "
            "wrapping both Kaartik and Kaavya into a warm, bouncy group hug on the cozy rug. "
            "Adorable Pixar 3D emotional comedy climax, smooth 3D character animation, bright saturated primary colors, soft volumetric glow. "
            "STRICTLY NO 2D drawings, NO pencil lines, NO comic text bubbles, NO flat illustrations."
        ),
        "outfile": RAW_CLIPS / "ep18_3d_p3.mp4"
    }
]

def setup_page_canvas(page, slot_idx, email):
    url = f"https://flow.google.com/u/{slot_idx}/"
    print(f"[*] [Slot {slot_idx} - {email}] Navigating to {url}...", flush=True)
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(3000)

    # Click "+ New project"
    new_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i]").first
    if new_btn.count() > 0 and new_btn.is_visible():
        new_btn.click()
        page.wait_for_timeout(4000)

    print(f"[+] [Slot {slot_idx}] Canvas ready: {page.url}", flush=True)

    # Configure Tune settings to Never confirm & 9:16
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
            print(f"[!] [Slot {slot_idx}] Tune config warning: {e}", flush=True)

def submit_prompt_to_page(page, slot_idx, prompt_text, part_num):
    print(f"[*] [Slot {slot_idx}] Submitting Prompt for Scene {part_num}...", flush=True)
    editor = page.locator("[contenteditable='true'], div.ProseMirror, textarea").first
    if editor.count() > 0:
        editor.click()
        page.wait_for_timeout(300)
        editor.fill(prompt_text)
        page.wait_for_timeout(500)
        send_btn = page.locator("button:has-text('arrow_forward'), button[aria-label*='Submit' i], button.send-button").first
        if send_btn.count() > 0 and send_btn.is_visible():
            send_btn.click()
        else:
            page.keyboard.press("Enter")
        print(f"[🚀 SENT] [Slot {slot_idx}] Scene {part_num} prompt dispatched!", flush=True)

def handle_approvals(page, slot_idx, part_num):
    target = page.locator("button:has-text('Always approve'), [role='button']:has-text('Always approve'), div:has-text('Always approve')")
    if target.count() > 0 and target.last.is_visible():
        print(f"[✓] [Slot {slot_idx}] Auto-approving credits...", flush=True)
        target.last.click(force=True)
        page.wait_for_timeout(1000)
        return
    app_target = page.locator("button:has-text('Approve'), [role='button']:has-text('Approve')")
    if app_target.count() > 0 and app_target.last.is_visible():
        print(f"[✓] [Slot {slot_idx}] Approving credits...", flush=True)
        app_target.last.click(force=True)
        page.wait_for_timeout(1000)

def download_video_clip(page, slot_idx, part_num, out_path):
    print(f"[*] [Slot {slot_idx} - Scene {part_num}] Attempting download...", flush=True)
    cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video")
    if cards.count() > 0:
        cards.last.click(force=True)
        page.wait_for_timeout(2500)
        
        dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
        if dl_btn.count() > 0 and dl_btn.is_visible():
            dl_btn.click(force=True)
            page.wait_for_timeout(1500)
            
            target_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size')").first
            if target_720.count() > 0:
                print(f"[+] [Slot {slot_idx}] Triggering 720p download -> {out_path}...", flush=True)
                with page.expect_download(timeout=60000) as dl_info:
                    target_720.click(force=True)
                dl = dl_info.value
                dl.save_as(str(out_path))
                print(f"[🏆] [Slot {slot_idx} - Scene {part_num}] SAVED: {out_path.name} ({out_path.stat().st_size} bytes)", flush=True)
                return True
                
    # Fallback direct download button
    dl_direct = page.locator("button[aria-label='Download media'], button[aria-label*='download' i]").first
    if dl_direct.count() > 0 and dl_direct.is_visible():
        dl_direct.click(force=True)
        page.wait_for_timeout(1000)
        target_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p')").first
        if target_720.count() > 0:
            with page.expect_download(timeout=60000) as dl_info:
                target_720.click(force=True)
            dl = dl_info.value
            dl.save_as(str(out_path))
            print(f"[🏆] [Slot {slot_idx} - Scene {part_num}] SAVED: {out_path.name} ({out_path.stat().st_size} bytes)", flush=True)
            return True
            
    print(f"[!] [Slot {slot_idx} - Scene {part_num}] Download failed to trigger.", flush=True)
    page.screenshot(path=str(BASE_DIR / "data" / f"dl_error_slot_{slot_idx}.png"))
    return False

def stitch_scenes(scene_files, final_output):
    print("\n" + "=" * 60, flush=True)
    print("  STITCHING 3D COCOMELON SCENES INTO MASTER SHORT", flush=True)
    print("=" * 60, flush=True)
    
    concat_list = BASE_DIR / "data" / "concat_3d_ep18.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for sf in scene_files:
            f.write(f"file '{sf.resolve()}'\n")
            
    cmd = [
        "ffmpeg", "-y",
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
    
    print(f"[*] Running FFmpeg stitch: {' '.join(cmd)}", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and final_output.exists() and final_output.stat().st_size > 0:
        print(f"[🎉 MASTERPIECE READY] {final_output.name} ({final_output.stat().st_size / (1024*1024):.2f} MB)", flush=True)
        # Extract verification frame
        verify_frame = BASE_DIR / "data" / "ep18_cocomelon_test_frame.png"
        subprocess.run(["ffmpeg", "-y", "-ss", "00:00:03", "-i", str(final_output), "-vframes", "1", str(verify_frame)], capture_output=True)
        print(f"[📸 Verification Frame Saved]: {verify_frame}", flush=True)
        return True
    else:
        print(f"[!] FFmpeg stitch failed: {res.stderr}", flush=True)
        return False

def run_production():
    print("=" * 70, flush=True)
    print("  THE NAUGHTY DUO — COCOMELON 3D CGI PARALLEL PRODUCTION ENGINE", flush=True)
    print("  Slots: 2 (PRO Unlimited), 5, 6 | 100% 3D CGI Standards", flush=True)
    print("=" * 70, flush=True)

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            accept_downloads=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            args=["--disable-blink-features=AutomationControlled"]
        )

        active_sessions = []
        # Step 1: Open all 3 canvases
        for s in SCENES:
            page = ctx.new_page()
            setup_page_canvas(page, s["slot"], s["email"])
            active_sessions.append((page, s))

        # Step 2: Submit all 3 prompts simultaneously!
        print("\n" + "=" * 60, flush=True)
        print("  DISPATCHING ALL 3 COCOMELON 3D CGI PROMPTS SIMULTANEOUSLY", flush=True)
        print("=" * 60, flush=True)
        for page, s in active_sessions:
            submit_prompt_to_page(page, s["slot"], s["prompt"], s["part"])

        # Check approvals
        for _ in range(5):
            time.sleep(1)
            for page, s in active_sessions:
                handle_approvals(page, s["slot"], s["part"])

        # Step 3: Wait concurrently for rendering (~75-90s)
        print("\n[*] Monitoring all 3 renders concurrently (~80s)...", flush=True)
        start_time = time.time()
        for i in range(1, 20):
            time.sleep(5)
            elapsed = int(time.time() - start_time)
            status_line = []
            for page, s in active_sessions:
                stop_btn = page.locator("button:has-text('Stop'), button[aria-label='Stop']")
                is_rendering = stop_btn.count() > 0 and stop_btn.first.is_visible()
                vids = page.locator("video, [aria-label*='Open video in editor' i]").count()
                status_line.append(f"Slot {s['slot']} (Scene {s['part']}): {'Render' if is_rendering else 'Ready'} ({vids} vids)")
            print(f"[{elapsed}s] " + " | ".join(status_line), flush=True)

        # Step 4: Download all 3 rendered scenes
        print("\n" + "=" * 60, flush=True)
        print("  DOWNLOADING HIGH-FIDELITY 3D CGI SCENES", flush=True)
        print("=" * 60, flush=True)
        downloaded_files = []
        for page, s in active_sessions:
            success = download_video_clip(page, s["slot"], s["part"], s["outfile"])
            if success and s["outfile"].exists():
                downloaded_files.append(s["outfile"])

        ctx.close()

        # Step 5: Stitch into Final Short
        if len(downloaded_files) == 3:
            final_mp4 = OUTPUT_DIR / "ep_18_magic_freeze_remote_final.mp4"
            stitch_success = stitch_scenes(downloaded_files, final_mp4)
            if stitch_success:
                print("\n[🎯 SUCCESS] Episode 18 CoComelon 3D CGI Short is fully produced!", flush=True)
                return True
        else:
            print(f"[!] Only {len(downloaded_files)}/3 scenes downloaded successfully.", flush=True)
            return False

if __name__ == "__main__":
    run_production()
