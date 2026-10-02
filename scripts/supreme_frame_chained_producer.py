import os
import sys
import time
import json
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
FFMPEG_BIN = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
GLOBAL_UPLOAD_LOG = Path(r"C:\TheNaughtyDuo_Automation\uploaded_videos_log.json")
LOCAL_UPLOAD_LOG = BASE_DIR / "data" / "uploaded_videos_log.json"

SLOT_IDX = 7
SLOT_EMAIL = "rkumar.ukb@gmail.com"

# Episode 07 - Golgappa Prank
EPISODE_ID = "ep_07_spicy_golgappa"
EPISODE_TITLE = "Mummy Ka Spicy Golgappa Prank! 🌶️😵 Mirchi Lag Gayi! #TheNaughtyDuo #shorts"
EPISODE_DESC = (
    "Mummy ne banaye the extra teekhe Golgappe! 🌶️😋\n"
    "Kaartik ne bina puche bada sa golgappa munh me daal liya... aur fir kaano se dhuwan nikal gaya! 😂\n"
    "Dekhiye Kaartik ka ye teekha reaction!\n\n"
    "Aapko teekha golgappa pasand hai ya meetha? Comment me batana! 👇❤️\n\n"
    "#shorts #TheNaughtyDuo #golgappaprank #panipuri #funnycartoon #3danimation #comedy #familycomedy #viralshorts"
)

# Scene Prompts adhering strictly to visual_style_lock.json (CoComelon & Pixar 3D CGI)
SCENE_PROMPTS = [
    {
        "part": 1,
        "label": "Part 1 - Greedy Kaartik Snatches the Giant Golgappa",
        "prompt": (
            "CoComelon and Pixar 3D animated style, 9:16 vertical orientation, 8 seconds. "
            "Full 3D CGI animation. Cozy sunlit Indian dining room. Exactly ONE chubby 3D toddler boy Kaartik "
            "(5 years old, rounded cute cheeks, big expressive glassy 3D brown eyes, volumetric black hair, bright yellow polo shirt, blue shorts) "
            "sneaks up to the wooden dining table with a mischievous grin. On the table sits a colorful platter of crispy golden puffed Golgappas "
            "and bowls of spicy dark-green mint water. Kaartik greedily reaches for the biggest crispy golgappa. "
            "Beside him, cute 3D toddler sister Kaavya (3.5 years old, chubby cheeks, curly hair, bright pink frock) giggles excitedly. "
            "Volumetric 3D lighting, glossy Pixar skin shaders, rich vibrant primary colors. "
            "STRICTLY NO 2D drawings, NO flat sketches, NO comic book outlines, NO speech bubbles, NO text."
        ),
        "outfile": RAW_CLIPS / "ep07_3d_p1.mp4",
        "last_frame": RAW_CLIPS / "ep07_3d_p1_last.png"
    },
    {
        "part": 2,
        "label": "Part 2 - The Spicy Explosion (Mirchi Lag Gayi!)",
        "prompt": (
            "CoComelon and Pixar 3D animated style, 9:16 vertical orientation, 8 seconds. "
            "Full 3D CGI animation. Modern Indian dining room. Continuous seamless scene. Exactly ONE chubby 3D toddler boy Kaartik "
            "(same yellow polo shirt, blue shorts, rounded cheeks) stuffs the giant spicy golgappa into his mouth! "
            "Instantly his eyes pop wide in hilarious cartoon spicy shock, cheeks turn glowing bright tomato red, and funny 3D steam puffs comically from his ears! "
            "Kaartik fans his open mouth with both hands jumping on his toes. Cute toddler sister Kaavya (pink frock) claps and laughs happily, "
            "playfully offering him a red ketchup bottle. Adorable Pixar 3D comedy animation, vibrant studio lighting. "
            "STRICTLY NO 2D drawings, NO flat art, NO comic speech bubbles, NO written text."
        ),
        "outfile": RAW_CLIPS / "ep07_3d_p2.mp4",
        "last_frame": RAW_CLIPS / "ep07_3d_p2_last.png"
    },
    {
        "part": 3,
        "label": "Part 3 - Cold Milk Relief & Joyful Family Hug",
        "prompt": (
            "CoComelon and Pixar 3D animated style, 9:16 vertical orientation, 8 seconds. "
            "Full 3D CGI animation. Modern Indian dining room. Continuous seamless scene. Beautiful 3D Indian mother Pinki "
            "(25 years old, smooth 3D features, powder-blue traditional kurti) rushes in laughing warmly with a tall glass of cold sweet milk! "
            "Kaartik (yellow polo) greedily gulps the cold milk, instantly relieved with a cute white milk mustache and blissful smile. "
            "Pinki wraps Kaartik and cute toddler sister Kaavya (pink frock) into a big, warm, bouncy family group hug on the cozy carpet. "
            "Heartwarming Pixar 3D family comedy climax, ultra-smooth fluid animation, bright cheerful colors, soft volumetric glow. "
            "STRICTLY NO 2D drawings, NO pencil sketches, NO speech bubbles, NO flat illustrations."
        ),
        "outfile": RAW_CLIPS / "ep07_3d_p3.mp4",
        "last_frame": RAW_CLIPS / "ep07_3d_p3_last.png"
    }
]

FINAL_MASTER_SHORT = OUTPUT_DIR / "ep_07_spicy_golgappa_final.mp4"

def extract_last_frame(input_video, output_image):
    print(f"[*] Extracting exact last frame from {input_video.name}...", flush=True)
    cmd = [
        FFMPEG_BIN, "-y",
        "-sseof", "-0.1",
        "-i", str(input_video),
        "-update", "1",
        "-q:v", "1",
        str(output_image)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and output_image.exists():
        print(f"[✓ Anchor Saved] {output_image.name} ({output_image.stat().st_size} bytes)", flush=True)
        return True
    else:
        print(f"[!] Last frame extraction failed: {res.stderr}", flush=True)
        return False

def configure_tune(page):
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
            print(f"[!] Tune warning: {e}", flush=True)

def handle_credit_approvals(page):
    for _ in range(3):
        target = page.locator("button:has-text('Always approve'), [role='button']:has-text('Always approve'), div:has-text('Always approve')")
        if target.count() > 0 and target.last.is_visible():
            target.last.click(force=True)
            print("[✓] Clicked 'Always approve'!", flush=True)
            page.wait_for_timeout(1000)
            return
        app_target = page.locator("button:has-text('Approve'), [role='button']:has-text('Approve')")
        if app_target.count() > 0 and app_target.last.is_visible():
            app_target.last.click(force=True)
            print("[✓] Clicked 'Approve'!", flush=True)
            page.wait_for_timeout(1000)
            return
        time.sleep(1)

def attach_anchor_frame(page, image_path):
    print(f"[*] Attaching Frame Chaining Anchor: {image_path.name}...", flush=True)
    plus_btn = page.locator("[aria-label*='Add ingredients' i]").last
    if plus_btn.count() == 0:
        plus_btn = page.locator("button:has-text('add')").last
    plus_btn.click()
    page.wait_for_timeout(1000)

    # Click Upload media with file chooser
    with page.expect_file_chooser() as fc_info:
        up_btn = page.locator("button:has-text('Upload media')").first
        if up_btn.count() == 0:
            up_btn = page.locator("div:has-text('Upload media')").first
        up_btn.click(force=True)

    fc = fc_info.value
    fc.set_files(str(image_path))
    print(f"[*] Anchor frame chosen: {image_path.name}. Waiting for upload...", flush=True)
    page.wait_for_timeout(5000)

    # Click Add to prompt
    add_to_prompt = page.locator("button:has-text('Add to prompt'), [role='button']:has-text('Add to prompt')").first
    if add_to_prompt.count() > 0:
        add_to_prompt.click(force=True)
        page.wait_for_timeout(1500)
        # Close any lingering modal/backdrop
        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)
        # If backdrop still exists, click it to dismiss
        backdrop = page.locator(".cdk-overlay-backdrop")
        if backdrop.count() > 0 and backdrop.first.is_visible():
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)
        print(f"[✓ Anchor Attached to Prompt]: {image_path.name}", flush=True)
        return True
    else:
        print("[!] Could not find 'Add to prompt' button after upload.", flush=True)
        page.keyboard.press("Escape")
        return False

def submit_prompt_and_wait(page, prompt_text, part_num, is_chained=False, anchor_image=None):
    print(f"\n" + "-" * 50, flush=True)
    print(f"[*] [Scene {part_num}] DISPATCHING GENERATION (Chained={is_chained})...", flush=True)
    print(f"-" * 50, flush=True)

    if is_chained and anchor_image and anchor_image.exists():
        attach_anchor_frame(page, anchor_image)

    editor = page.locator("[contenteditable='true'], div.ProseMirror, textarea").first
    editor.click()
    page.wait_for_timeout(300)
    editor.fill(prompt_text)
    page.wait_for_timeout(500)

    send_btn = page.locator("button:has-text('arrow_forward'), button[aria-label*='Submit' i], button.send-button").first
    if send_btn.count() > 0 and send_btn.is_visible():
        send_btn.click()
    else:
        page.keyboard.press("Enter")

    print(f"[🚀 SENT] Scene {part_num} prompt submitted to Google Flow!", flush=True)
    page.wait_for_timeout(2000)
    handle_credit_approvals(page)

def wait_for_video_ready(page, part_num, timeout_secs=120):
    print(f"[*] [Scene {part_num}] Waiting for video generation (~60-90s)...", flush=True)
    start_time = time.time()
    while time.time() - start_time < timeout_secs:
        handle_credit_approvals(page)
        # Check if completed video card exists and is not generating
        cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video")
        if cards.count() > 0:
            # Check if there is no active progress bar or spinner
            progress = page.locator("mat-progress-bar, [role='progressbar'], .loading-spinner")
            if progress.count() == 0 or not progress.first.is_visible():
                print(f"[✓] [Scene {part_num}] Render appears complete after {int(time.time() - start_time)}s!", flush=True)
                return True
        time.sleep(5)
    print(f"[!] [Scene {part_num}] Timed out after {timeout_secs}s, attempting download anyway...", flush=True)
    return False

def download_latest_video(page, part_num, out_path):
    print(f"[*] [Scene {part_num}] Downloading video to {out_path.name}...", flush=True)
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
                print(f"[+] [Scene {part_num}] Downloading 720p...", flush=True)
                with page.expect_download(timeout=60000) as dl_info:
                    target_720.click(force=True)
                dl = dl_info.value
                dl.save_as(str(out_path))
                print(f"[🏆 SAVED] Scene {part_num}: {out_path.name} ({out_path.stat().st_size} bytes)", flush=True)
                page.keyboard.press("Escape")
                page.wait_for_timeout(1000)
                return True

    # Fallback direct download
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
            print(f"[🏆 SAVED] Scene {part_num}: {out_path.name} ({out_path.stat().st_size} bytes)", flush=True)
            return True

    print(f"[!] [Scene {part_num}] Download failed.", flush=True)
    return False

def stitch_masterpiece(clips, output_file):
    print("\n" + "=" * 60, flush=True)
    print("  STITCHING 3D COCOMELON SCENES INTO SUPREME MASTER SHORT", flush=True)
    print("=" * 60, flush=True)
    concat_list = BASE_DIR / "data" / "concat_ep07.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for clip in clips:
            f.write(f"file '{clip.resolve()}'\n")

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
        str(output_file)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and output_file.exists() and output_file.stat().st_size > 0:
        print(f"[🎉 MASTERPIECE STITCHED]: {output_file.name} ({output_file.stat().st_size / (1024*1024):.2f} MB)", flush=True)
        return True
    else:
        print(f"[!] Stitching failed: {res.stderr}", flush=True)
        return False

def upload_to_youtube(video_path, title, description):
    print("\n" + "=" * 60, flush=True)
    print(f"  UPLOADING MASTERPIECE TO YOUTUBE SHORTS", flush=True)
    print(f"  Title: {title}", flush=True)
    print("=" * 60, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        print("[*] Navigating to YouTube Studio...", flush=True)
        page.goto("https://studio.youtube.com", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)

        skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
        if skip.count() > 0 and skip.is_visible():
            skip.click()
            page.wait_for_timeout(3000)

        create_btn = page.locator("ytcp-button#create-icon, button:has-text('Create'), ytcp-button:has-text('Create')").first
        if create_btn.count() > 0:
            create_btn.click()
            page.wait_for_timeout(1500)
            upload_option = page.get_by_text("Upload videos", exact=False).first
            if upload_option.count() > 0 and upload_option.is_visible():
                upload_option.click()
            page.wait_for_timeout(2000)
        else:
            arrow = page.locator("ytcp-button#upload-icon, button[aria-label*='Upload' i]").first
            if arrow.count() > 0:
                arrow.click()
                page.wait_for_timeout(2000)

        file_input = page.locator("input[type='file']").first
        if file_input.count() == 0:
            for f in page.frames:
                inp = f.locator("input[type='file']")
                if inp.count() > 0:
                    file_input = inp.first
                    break

        if file_input.count() == 0:
            print("[!] File input element not found.", flush=True)
            browser.close()
            return None

        print(f"[+] Uploading video file: {video_path}...", flush=True)
        file_input.set_input_files(str(video_path))
        page.wait_for_timeout(8000)

        video_link = None
        for _ in range(15):
            links = page.locator("a.ytcp-video-info, a[href*='youtu.be'], a[href*='youtube.com/shorts']")
            if links.count() > 0:
                for idx in range(links.count()):
                    href = links.nth(idx).get_attribute("href")
                    if href and ("youtu.be" in href or "shorts" in href):
                        video_link = href
                        break
            if video_link:
                break
            page.wait_for_timeout(1000)

        print(f"[+] Video Link detected: {video_link}", flush=True)

        # Title
        title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        if title_box.count() > 0:
            title_box.click()
            page.wait_for_timeout(300)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            title_box.fill(title[:100])
            page.wait_for_timeout(500)
            print("[+] Title filled!", flush=True)

        # Description
        desc_box = page.locator("#description-textarea div#textbox, ytcp-mention-textbox#description-textarea div#textbox, #textbox[aria-label*='description' i]").first
        if desc_box.count() == 0:
            tbs = page.locator("#textbox")
            if tbs.count() >= 2:
                desc_box = tbs.nth(1)

        if desc_box.count() > 0:
            desc_box.click()
            page.wait_for_timeout(300)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            desc_box.fill(description)
            page.wait_for_timeout(500)
            print("[+] Description filled!", flush=True)

        # Audience: Not made for kids
        not_kids = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
        if not_kids.count() > 0:
            not_kids.click()
            page.wait_for_timeout(500)
            print("[+] Audience set: Not made for kids.", flush=True)

        # Next x3
        for step in range(3):
            next_btn = page.locator("ytcp-button#next-button, button:has-text('Next')").first
            if next_btn.count() > 0 and next_btn.is_visible() and next_btn.is_enabled():
                next_btn.click()
                print(f"[+] Clicked Next ({step+1}/3)", flush=True)
                page.wait_for_timeout(2500)

        # PUBLIC
        pub_radio = page.locator("ytcp-uploads-dialog tp-yt-paper-radio-button[name='PUBLIC'], tp-yt-paper-radio-button[name='PUBLIC']").first
        if pub_radio.count() > 0:
            pub_radio.click(force=True)
            print("[+] Visibility set: PUBLIC.", flush=True)
            page.wait_for_timeout(1500)

        # Publish
        publish_btn = page.locator("ytcp-uploads-dialog ytcp-button#done-button, ytcp-uploads-dialog button:has-text('Publish'), ytcp-uploads-dialog #publish-button").first
        if publish_btn.count() == 0:
            publish_btn = page.locator("button:has-text('Publish')").first
        if publish_btn.count() > 0:
            publish_btn.click(force=True)
            print("[+] Clicked Publish!", flush=True)
            page.wait_for_timeout(4000)

        pub_anyway = page.locator("button:has-text('Publish anyway'), ytcp-button:has-text('Publish anyway')").first
        if pub_anyway.count() > 0 and pub_anyway.is_visible():
            print("[+] Clicking 'Publish anyway' modal...", flush=True)
            pub_anyway.click(force=True)
            page.wait_for_timeout(4000)

        if not video_link:
            dialog_links = page.locator("ytcp-video-share-dialog a, a[href*='youtu.be']")
            if dialog_links.count() > 0:
                for i in range(dialog_links.count()):
                    href = dialog_links.nth(i).get_attribute("href")
                    if href and "youtu.be" in href:
                        video_link = href
                        break

        browser.close()
        return video_link

def sync_logs_and_dashboard(video_url, episode_id, title, filepath):
    entry = {
        "key": episode_id,
        "filename": filepath.name,
        "size_mb": round(filepath.stat().st_size / (1024 * 1024), 2),
        "youtube": video_url,
        "youtube_title": title,
        "visual_style": "100% 3D CGI CoComelon & Pixar (Frame-Chained Strict Consistency)",
        "continuity_method": "Last-Frame Image-to-Video Anchor (FFmpeg -> Flow Canvas)",
        "youtube_status": "LIVE",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    for log_path in [GLOBAL_UPLOAD_LOG, LOCAL_UPLOAD_LOG]:
        try:
            if log_path.exists():
                data = json.loads(log_path.read_text(encoding="utf-8"))
            else:
                data = {"uploaded": []}
            data.setdefault("uploaded", []).append(entry)
            log_path.write_text(json.dumps(data, indent=4), encoding="utf-8")
            print(f"[✓ Synced Log]: {log_path}", flush=True)
        except Exception as e:
            print(f"[!] Log sync warning for {log_path}: {e}", flush=True)

def main():
    print("=" * 70, flush=True)
    print("  THE NAUGHTY DUO — SUPREME FRAME-CHAINED 3D CGI PRODUCER")
    print(f"  Episode: {EPISODE_ID} ({EPISODE_TITLE})")
    print(f"  Account: Slot {SLOT_IDX} ({SLOT_EMAIL})")
    print("  Continuity: 100% Last-Frame Image-to-Video Chaining")
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
        page = ctx.new_page()
        page.goto(f"https://flow.google.com/u/{SLOT_IDX}/", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(3000)

        # New project
        new_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i]").first
        if new_btn.count() > 0 and new_btn.is_visible():
            new_btn.click()
            page.wait_for_timeout(4000)

        print(f"[+] Fresh Project Canvas: {page.url}", flush=True)
        configure_tune(page)

        # STEP 1: SCENE 1
        s1 = SCENE_PROMPTS[0]
        if s1["outfile"].exists() and s1["outfile"].stat().st_size > 1000000:
            print(f"[✓ Reusing Existing Scene 1]: {s1['outfile'].name} ({s1['outfile'].stat().st_size} bytes)", flush=True)
            s1_ok = True
        else:
            submit_prompt_and_wait(page, s1["prompt"], part_num=1, is_chained=False)
            time.sleep(65)
            wait_for_video_ready(page, part_num=1, timeout_secs=90)
            s1_ok = download_latest_video(page, part_num=1, out_path=s1["outfile"])
            if not s1_ok:
                print("[!] Scene 1 download failed. Retrying in 15s...", flush=True)
                time.sleep(15)
                s1_ok = download_latest_video(page, part_num=1, out_path=s1["outfile"])

        if not s1_ok:
            print("[CRITICAL] Could not get Scene 1. Aborting.", flush=True)
            ctx.close()
            return

        # EXTRACT SCENE 1 LAST FRAME
        if not s1["last_frame"].exists():
            extract_last_frame(s1["outfile"], s1["last_frame"])
        else:
            print(f"[✓ Reusing Anchor 1]: {s1['last_frame'].name}", flush=True)

        # STEP 2: SCENE 2 (Chained from Scene 1 Last Frame)
        s2 = SCENE_PROMPTS[1]
        if s2["outfile"].exists() and s2["outfile"].stat().st_size > 1000000:
            print(f"[✓ Reusing Existing Scene 2]: {s2['outfile'].name}", flush=True)
            s2_ok = True
        else:
            submit_prompt_and_wait(page, s2["prompt"], part_num=2, is_chained=True, anchor_image=s1["last_frame"])
            time.sleep(65)
            wait_for_video_ready(page, part_num=2, timeout_secs=90)
            s2_ok = download_latest_video(page, part_num=2, out_path=s2["outfile"])
            if not s2_ok:
                print("[!] Scene 2 download failed. Retrying in 15s...", flush=True)
                time.sleep(15)
                s2_ok = download_latest_video(page, part_num=2, out_path=s2["outfile"])

        if not s2_ok:
            print("[CRITICAL] Could not download Scene 2. Aborting.", flush=True)
            ctx.close()
            return

        # EXTRACT SCENE 2 LAST FRAME
        if not s2["last_frame"].exists():
            extract_last_frame(s2["outfile"], s2["last_frame"])
        else:
            print(f"[✓ Reusing Anchor 2]: {s2['last_frame'].name}", flush=True)

        # STEP 3: SCENE 3 (Chained from Scene 2 Last Frame)
        s3 = SCENE_PROMPTS[2]
        if s3["outfile"].exists() and s3["outfile"].stat().st_size > 1000000:
            print(f"[✓ Reusing Existing Scene 3]: {s3['outfile'].name}", flush=True)
            s3_ok = True
        else:
            submit_prompt_and_wait(page, s3["prompt"], part_num=3, is_chained=True, anchor_image=s2["last_frame"])
            time.sleep(65)
            wait_for_video_ready(page, part_num=3, timeout_secs=90)
            s3_ok = download_latest_video(page, part_num=3, out_path=s3["outfile"])
            if not s3_ok:
                print("[!] Scene 3 download failed. Retrying in 15s...", flush=True)
                time.sleep(15)
                s3_ok = download_latest_video(page, part_num=3, out_path=s3["outfile"])

        if not s3_ok:
            print("[CRITICAL] Could not download Scene 3. Aborting.", flush=True)
            ctx.close()
            return

        ctx.close()

    # STEP 4: STITCH MASTERPIECE
    stitched_clips = [s1["outfile"], s2["outfile"], s3["outfile"]]
    stitch_ok = stitch_masterpiece(stitched_clips, FINAL_MASTER_SHORT)
    if not stitch_ok:
        print("[CRITICAL] Stitching failed. Aborting upload.", flush=True)
        return

    # STEP 5: UPLOAD TO YOUTUBE SHORTS
    video_url = upload_to_youtube(FINAL_MASTER_SHORT, EPISODE_TITLE, EPISODE_DESC)
    if video_url:
        print(f"\n[🚀 PUBLISHED SUCCESSFULLY TO YOUTUBE SHORTS]: {video_url}", flush=True)
        sync_logs_and_dashboard(video_url, EPISODE_ID, EPISODE_TITLE, FINAL_MASTER_SHORT)
    else:
        print("[!] Upload returned without explicit short link. Please check YouTube Studio.", flush=True)

if __name__ == "__main__":
    main()
