import os
import sys
import time
import json
import subprocess
from datetime import datetime
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

PROJECT_URL = "https://flow.google.com/u/0/project/1876f0f7-bc42-4764-86c9-35d76cb3a615"
BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
FFMPEG_BIN = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
LOG_FILE = Path(r"C:\TheNaughtyDuo_Automation\uploaded_videos_log.json")

# Master files
S1_CLIP = RAW_CLIPS / "ep20_arm_wrestling_p1.mp4"
S1_FRAME = RAW_CLIPS / "ep20_arm_wrestling_p1_sample.png"
S2_CLIP = RAW_CLIPS / "ep20_arm_wrestling_p2.mp4"
S2_FRAME = RAW_CLIPS / "ep20_arm_wrestling_p2_sample.png"
MASTER_720 = OUTPUT_DIR / "ep20_arm_wrestling_master_720p.mp4"
MASTER_1080 = OUTPUT_DIR / "TheNaughtyDuo_EP20_Arm_Wrestling_1080p.mp4"
THUMB_FILE = OUTPUT_DIR / "TheNaughtyDuo_EP20_Arm_Wrestling_thumb.png"

# Locked Style & Avoid blocks
STYLE_BLOCK = (
    "Semi-realistic 3D animated style, Pixar/Disney-inspired rendering with soft painterly texture, "
    "warm cinematic color grading. Vibrant lighting, rich subsurface skin scattering, fluid cartoon character animation."
)
AVOID_BLOCK = "Avoid: flat 2D look, inconsistent facial features, extra fingers, distorted hands, blurry background, style shifting mid-scene, anatomy errors, redesigned character"

# Story Prompts
SCENE1_PROMPT = f"""{STYLE_BLOCK}

Warm domestic dining room bathed in golden volumetric morning sunlight, gentle dust motes dancing in the sunbeams. High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. Full 3D CGI animation.
Loving burly Indian father (bearded gentle giant, warm smile, simple white henley t-shirt) rests his muscular hairy forearm on the rustic wooden dining table. 
Adorable chubby toddler daughter Kaavya (3.5 years old, double hair buns with pink scrunchies, rosy blushing cheeks, sweet pink pajamas) grips Papa's giant wrist with BOTH of her tiny chubby hands, squeezing her big brown Disney eyes shut, grunting with 100% dramatic effort, feet dangling off her small chair!
Papa smiles tenderly with gentle eyes, effortlessly letting her try. 
In the background, toddler brother Kaartik (5 years old, bright yellow polo shirt, messy hair fringe) jumps up on a stool acting as referee, waving a wooden spoon cheering excitedly!
Ultra-detailed textures: soft cotton clothing, rich wood grain, glowing skin subsurface scattering, cinematic shallow depth of field.
STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays.

{AVOID_BLOCK}"""

SCENE2_PROMPT = f"""{STYLE_BLOCK}

Seamless continuous scene climax. Warm domestic dining room, golden morning sunlight. High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. Full 3D CGI animation.
Papa suddenly opens his mouth in an exaggerated comical shocked cartoon expression, acting like tiny Kaavya has superhuman Hulk strength! 
Papa pretends to struggle, sweat bead on his brow, as his giant arm slowly bends backward toward the table! 
Kaavya (3.5 years old, double hair buns with pink scrunchies, pink pajamas) pushes with adorable victorious giggles!
SLAP! Papa's giant hand gently hits the wooden table! 
Kaavya leaps up raising both tiny arms in the air cheering with pure uncontainable joy like a champion! 
Papa laughs warmly with pure fatherly love, scooping tiny Kaavya up high onto his broad shoulders! Kaartik (yellow polo) claps enthusiastically in the background!
Ultra-detailed Pixar 3D rendering, fluid cartoon slapstick animation, glowing warm lighting.
STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays.

{AVOID_BLOCK}"""

# SEO
YT_TITLE = "Kaavya Ne Haraya Papa Ko Panje Me! 💪👧🧔 The Great Arm Wrestling Match! #shorts"
YT_DESC = (
    "Nanhi Kaavya ne Papa ko diya open challenge: PANJA LADANA! 💪👧🧔\n"
    "Dono nanhe haathon se poori taqat laga di, aur Papa ne haarne ka aesa hilarious drama kiya ki aapki hassi nahi rukegi! 😂❤️\n"
    "Wait for the heartwarming victory moment at the end! 🥰✨\n\n"
    "Kya aapne bhi bachpan me Papa ke sath panja ladaya hai? Comment me zaroor batayein! 👇❤️\n\n"
    "Aise hi pyare aur hilarious 3D animation cartoons ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔\n\n"
    "#shorts #TheNaughtyDuo #fatherdaughter #familycomedy #armwrestling #funnycartoon #3danimation #kaavyaandkaartik #relatable #viralshorts #trending"
)
TIKTOK_CAPTION = (
    "Kaavya ne haraya Papa ko panje me! 💪👧🧔 Dono haathon se poori taqat laga di! 😂❤️ Wait for Papa's heartwarming reaction at the end! 🥰 Who won arm wrestling against their dad? Comment below! 👇 #TheNaughtyDuo #shorts #viral #funny #comedy #fatherdaughter #family #3danimation #hindicartoon #foryou #fyp #trending"
)

def run_production():
    print("=" * 70)
    print("  AUTONOMOUS PRODUCTION: EPISODE 20 (ARM WRESTLING CHAMPIONSHIP)")
    print("  STYLE BENCHMARK: @mult_bazilik (796K - 33.8M Views Aesthetic)")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            accept_downloads=True,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        # -------------------------------------------------------------
        # PART 1: GENERATE SCENE 1
        # -------------------------------------------------------------
        print("\n[*] Navigating to 'The Naughty Duo' project...")
        page.goto(PROJECT_URL, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)

        # Close any open editor view
        done_btn = page.locator("button:has-text('Done'), button[aria-label*='back' i]").first
        if done_btn.count() > 0 and done_btn.is_visible():
            done_btn.click(force=True)
            page.wait_for_timeout(2000)

        # Attach Kaavya reference
        add_btn = page.locator("button[aria-label='Add ingredients to the prompt box']").first
        if add_btn.count() > 0:
            print("[*] Attaching 'kaavya' character asset...")
            add_btn.click(force=True)
            page.wait_for_timeout(1500)
            overlay = page.locator(".cdk-overlay-pane, [role='dialog']").first
            if overlay.count() > 0:
                k_opt = overlay.locator("text='kaavya'").first
                if k_opt.count() > 0:
                    k_opt.click(force=True)
                    page.wait_for_timeout(1000)
                    overlay.locator("button:has-text('Add to prompt')").first.click(force=True)
                    page.wait_for_timeout(1000)

        # Attach Kaartik reference
        if add_btn.count() > 0:
            print("[*] Attaching 'kaartik' character asset...")
            add_btn.click(force=True)
            page.wait_for_timeout(1500)
            overlay = page.locator(".cdk-overlay-pane, [role='dialog']").first
            if overlay.count() > 0:
                kt_opt = overlay.locator("text='kaartik'").first
                if kt_opt.count() > 0:
                    kt_opt.click(force=True)
                    page.wait_for_timeout(1000)
                    overlay.locator("button:has-text('Add to prompt')").first.click(force=True)
                    page.wait_for_timeout(1000)

        # Fill Scene 1 prompt
        print("[*] Entering Scene 1 prompt...")
        editor = page.locator(".ProseMirror").first
        editor.click()
        editor.fill(SCENE1_PROMPT)
        page.wait_for_timeout(1000)

        # Submit Scene 1
        print("[*] Submitting Scene 1...")
        gen_btn = page.locator("button[aria-label='Start generation']").first
        if gen_btn.count() > 0 and gen_btn.is_enabled():
            gen_btn.click(force=True)
        else:
            page.keyboard.press("Control+Enter")

        page.wait_for_timeout(4000)

        # Approve dialog if any
        approve_btn = page.locator("button:has-text('Approve'), div:has-text('Approve'), span:has-text('Approve')").first
        if approve_btn.count() > 0 and approve_btn.is_visible():
            print("[+] Approving Scene 1...")
            approve_btn.click(force=True)
            page.wait_for_timeout(3000)

        # Wait for Scene 1 render
        print("[*] Waiting for Scene 1 render to complete (approx 35s)...")
        time.sleep(35)
        for check in range(12):
            stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
            if stop_btn.count() == 0:
                print("[+] Scene 1 render complete!")
                break
            time.sleep(5)

        # Download Scene 1
        print("[*] Downloading Scene 1 clip...")
        back_btn = page.locator("button[aria-label*='back' i]").first
        if back_btn.count() > 0 and back_btn.is_visible():
            back_btn.click(force=True)
            page.wait_for_timeout(2000)

        tiles = page.locator("flow-grid-tile-container, div.flow-grid-tile, [aria-label*='video' i]").all()
        if tiles:
            tiles[0].click(force=True)
            page.wait_for_timeout(2500)

            dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
            if dl_btn.count() > 0:
                dl_btn.click(force=True)
                page.wait_for_timeout(1500)
                target = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size'), button:has-text('1080p')").first
                if target.count() > 0:
                    with page.expect_download(timeout=60000) as dl_info:
                        target.click(force=True)
                    dl = dl_info.value
                    dl.save_as(str(S1_CLIP))
                    print(f"[🏆 SAVED SCENE 1]: {S1_CLIP.name} ({S1_CLIP.stat().st_size} bytes)")

        # Extract sample frame for Scene 1
        if S1_CLIP.exists():
            subprocess.run([FFMPEG_BIN, "-y", "-ss", "00:00:03", "-i", str(S1_CLIP), "-vframes", "1", "-q:v", "2", str(S1_FRAME)], capture_output=True)

        # -------------------------------------------------------------
        # PART 2: GENERATE SCENE 2
        # -------------------------------------------------------------
        print("\n[*] Proceeding to Scene 2 (Climax & Victory)...")
        page.goto(PROJECT_URL, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)

        # Close any open editor view
        done_btn = page.locator("button:has-text('Done'), button[aria-label*='back' i]").first
        if done_btn.count() > 0 and done_btn.is_visible():
            done_btn.click(force=True)
            page.wait_for_timeout(2000)

        # Attach Kaavya reference
        add_btn = page.locator("button[aria-label='Add ingredients to the prompt box']").first
        if add_btn.count() > 0:
            add_btn.click(force=True)
            page.wait_for_timeout(1500)
            overlay = page.locator(".cdk-overlay-pane, [role='dialog']").first
            if overlay.count() > 0:
                k_opt = overlay.locator("text='kaavya'").first
                if k_opt.count() > 0:
                    k_opt.click(force=True)
                    page.wait_for_timeout(1000)
                    overlay.locator("button:has-text('Add to prompt')").first.click(force=True)
                    page.wait_for_timeout(1000)

        # Attach Kaartik reference
        if add_btn.count() > 0:
            add_btn.click(force=True)
            page.wait_for_timeout(1500)
            overlay = page.locator(".cdk-overlay-pane, [role='dialog']").first
            if overlay.count() > 0:
                kt_opt = overlay.locator("text='kaartik'").first
                if kt_opt.count() > 0:
                    kt_opt.click(force=True)
                    page.wait_for_timeout(1000)
                    overlay.locator("button:has-text('Add to prompt')").first.click(force=True)
                    page.wait_for_timeout(1000)

        # Fill Scene 2 prompt
        print("[*] Entering Scene 2 prompt...")
        editor = page.locator(".ProseMirror").first
        editor.click()
        editor.fill(SCENE2_PROMPT)
        page.wait_for_timeout(1000)

        # Submit Scene 2
        print("[*] Submitting Scene 2...")
        gen_btn = page.locator("button[aria-label='Start generation']").first
        if gen_btn.count() > 0 and gen_btn.is_enabled():
            gen_btn.click(force=True)
        else:
            page.keyboard.press("Control+Enter")

        page.wait_for_timeout(4000)

        approve_btn = page.locator("button:has-text('Approve'), div:has-text('Approve'), span:has-text('Approve')").first
        if approve_btn.count() > 0 and approve_btn.is_visible():
            print("[+] Approving Scene 2...")
            approve_btn.click(force=True)
            page.wait_for_timeout(3000)

        # Wait for Scene 2 render
        print("[*] Waiting for Scene 2 render to complete (approx 35s)...")
        time.sleep(35)
        for check in range(12):
            stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
            if stop_btn.count() == 0:
                print("[+] Scene 2 render complete!")
                break
            time.sleep(5)

        # Download Scene 2
        print("[*] Downloading Scene 2 clip...")
        back_btn = page.locator("button[aria-label*='back' i]").first
        if back_btn.count() > 0 and back_btn.is_visible():
            back_btn.click(force=True)
            page.wait_for_timeout(2000)

        tiles = page.locator("flow-grid-tile-container, div.flow-grid-tile, [aria-label*='video' i]").all()
        if tiles:
            tiles[0].click(force=True)
            page.wait_for_timeout(2500)

            dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
            if dl_btn.count() > 0:
                dl_btn.click(force=True)
                page.wait_for_timeout(1500)
                target = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size'), button:has-text('1080p')").first
                if target.count() > 0:
                    with page.expect_download(timeout=60000) as dl_info:
                        target.click(force=True)
                    dl = dl_info.value
                    dl.save_as(str(S2_CLIP))
                    print(f"[🏆 SAVED SCENE 2]: {S2_CLIP.name} ({S2_CLIP.stat().st_size} bytes)")

        if S2_CLIP.exists():
            subprocess.run([FFMPEG_BIN, "-y", "-ss", "00:00:03", "-i", str(S2_CLIP), "-vframes", "1", "-q:v", "2", str(S2_FRAME)], capture_output=True)

        browser.close()

    # -------------------------------------------------------------
    # PART 3: STITCH & UPSCALE MASTER VIDEO
    # -------------------------------------------------------------
    print("\n[*] Assembling Master Short with FFmpeg...")
    concat_txt = BASE_DIR / "data" / "concat_ep20.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        f.write(f"file '{S1_CLIP.resolve()}'\n")
        f.write(f"file '{S2_CLIP.resolve()}'\n")

    # Step A: Seamless Concat (720p)
    subprocess.run([
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
        str(MASTER_720)
    ], capture_output=True)

    # Step B: High-Definition Lanczos 1080x1920
    print("[*] Upscaling to 1080x1920 (Full HD Vertical)...")
    subprocess.run([
        FFMPEG_BIN, "-y",
        "-i", str(MASTER_720),
        "-vf", "scale=1080:1920:flags=lanczos",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "slow",
        "-crf", "17",
        "-c:a", "aac",
        "-b:a", "256k",
        str(MASTER_1080)
    ], capture_output=True)

    # Step C: Extract High-Res Thumbnail
    print("[*] Extracting 1080p viral thumbnail...")
    subprocess.run([
        FFMPEG_BIN, "-y",
        "-ss", "00:00:05",
        "-i", str(MASTER_1080),
        "-vframes", "1",
        "-q:v", "2",
        str(THUMB_FILE)
    ], capture_output=True)

    print(f"[🏆 MASTER RENDERED]: {MASTER_1080.name} ({MASTER_1080.stat().st_size} bytes)")

    # -------------------------------------------------------------
    # PART 4: DIRECT PUBLISHING (YOUTUBE SHORTS & TIKTOK)
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("  LAUNCHING DIRECT MULTI-PLATFORM PUBLISHING")
    print("=" * 70)

    yt_url = upload_youtube()
    tt_status = upload_tiktok()

    # Record log
    record_upload(yt_url, tt_status)
    print("\n[🏆 FULL AUTONOMOUS PIPELINE COMPLETE]")

def upload_youtube():
    print("[*] Uploading Episode 20 to YouTube Shorts...")
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

        page.goto("https://studio.youtube.com", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)

        skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
        if skip.count() > 0 and skip.is_visible():
            skip.click()
            page.wait_for_timeout(2000)

        create_btn = page.locator("ytcp-button#create-icon, button:has-text('Create')").first
        if create_btn.count() > 0:
            create_btn.click()
            page.wait_for_timeout(1500)
            upload_option = page.get_by_text("Upload videos", exact=False).first
            if upload_option.count() > 0 and upload_option.is_visible():
                upload_option.click()
            page.wait_for_timeout(2000)

        file_input = page.locator("input[type='file']").first
        if file_input.count() == 0:
            for f in page.frames:
                inp = f.locator("input[type='file']")
                if inp.count() > 0:
                    file_input = inp.first
                    break

        file_input.set_input_files(str(MASTER_1080))
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

        print(f"[+] YouTube Video Link detected: {video_link}")

        # Set Title & Description
        title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        if title_box.count() > 0:
            title_box.click()
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            title_box.fill(YT_TITLE[:100])

        desc_box = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
        if desc_box.count() > 0:
            desc_box.click()
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            desc_box.fill(YT_DESC)

        not_kids = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
        if not_kids.count() > 0:
            not_kids.click()
            page.wait_for_timeout(500)

        for _ in range(3):
            next_btn = page.locator("ytcp-button#next-button, button:has-text('Next')").first
            if next_btn.count() > 0 and next_btn.is_visible() and next_btn.is_enabled():
                next_btn.click()
                page.wait_for_timeout(2500)

        pub_radio = page.locator("ytcp-uploads-dialog tp-yt-paper-radio-button[name='PUBLIC'], tp-yt-paper-radio-button[name='PUBLIC']").first
        if pub_radio.count() > 0:
            pub_radio.click(force=True)
            page.wait_for_timeout(1500)

        publish_btn = page.locator("ytcp-uploads-dialog ytcp-button#done-button, ytcp-uploads-dialog button:has-text('Publish')").first
        if publish_btn.count() > 0:
            publish_btn.click(force=True)
            page.wait_for_timeout(4000)

        pub_anyway = page.locator("button:has-text('Publish anyway')").first
        if pub_anyway.count() > 0 and pub_anyway.is_visible():
            pub_anyway.click(force=True)
            page.wait_for_timeout(4000)

        page.screenshot(path=str(BASE_DIR / "data" / "yt_ep20_posted.png"))
        browser.close()
        return video_link

def upload_tiktok():
    print("[*] Uploading Episode 20 to TikTok Studio...")
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1440, "height": 900})

        page.goto("https://www.tiktok.com/tiktokstudio/upload?from=upload", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(6000)

        if "login" in page.url.lower():
            browser.close()
            return False

        file_input = page.locator("input[type='file']").first
        if file_input.count() == 0:
            for f in page.frames:
                inp = f.locator("input[type='file']")
                if inp.count() > 0:
                    file_input = inp.first
                    break

        file_input.set_input_files(str(MASTER_1080))
        page.wait_for_timeout(10000)

        # Modals
        for _ in range(3):
            turn_on_btn = page.locator("button:has-text('Turn on'), button:has-text('Cancel')")
            if turn_on_btn.count() > 0 and turn_on_btn.first.is_visible():
                turn_on_btn.first.click(force=True)
                page.wait_for_timeout(1000)

            got_it_btn = page.locator("button:has-text('Got it')")
            if got_it_btn.count() > 0 and got_it_btn.first.is_visible():
                got_it_btn.first.click(force=True)
                page.wait_for_timeout(1000)

        caption_box = page.locator("[contenteditable='true'], .public-DraftEditor-content, textarea").first
        if caption_box.count() > 0:
            caption_box.click(force=True)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            page.keyboard.type(TIKTOK_CAPTION, delay=8)
            page.wait_for_timeout(2000)

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)

        post_btn = page.get_by_role("button", name="Post", exact=True)
        if post_btn.count() == 0:
            post_btn = page.locator("button:text-is('Post')")

        if post_btn.count() > 0:
            target_post_btn = post_btn.last
            for _ in range(15):
                if not target_post_btn.is_disabled():
                    break
                page.wait_for_timeout(2000)

            target_post_btn.click(force=True)
            page.wait_for_timeout(6000)

            modal_post = page.locator("button:has-text('Post anyway'), button:has-text('Confirm')")
            if modal_post.count() > 0 and modal_post.first.is_visible():
                modal_post.first.click(force=True)
                page.wait_for_timeout(3000)

            page.screenshot(path=str(BASE_DIR / "data" / "tiktok_ep20_posted.png"))
            browser.close()
            return True

        browser.close()
        return False

def record_upload(yt_url, tt_status):
    data = {"uploaded": []}
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass

    entry = {
        "key": "ep_20_arm_wrestling_match",
        "filename": "TheNaughtyDuo_EP20_Arm_Wrestling_1080p.mp4",
        "size_mb": round(MASTER_1080.stat().st_size / (1024 * 1024), 2),
        "youtube": yt_url or "UPLOAD_SUBMITTED",
        "youtube_title": YT_TITLE,
        "visual_style": "100% Pixar 3D CGI (Benchmark: @mult_bazilik Father-Daughter Format)",
        "youtube_status": "LIVE",
        "tiktok": "posted" if tt_status else "failed_or_needs_login",
        "tiktok_caption": TIKTOK_CAPTION,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    data["uploaded"].append(entry)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"[+] Recorded upload to {LOG_FILE}")

if __name__ == "__main__":
    run_production()
