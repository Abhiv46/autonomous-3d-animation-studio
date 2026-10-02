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

FFMPEG_BIN = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

EPISODE_ID = "ep_06_toy_mouse"
TITLE = "Ghar Me Aaya Nakli Chuha! 🐭😱 Kaartik Ka Prank Backfire! #TheNaughtyDuo #shorts"
DESCRIPTION = """Kaartik ne Mummy ko darane ke liye chhoda nakli toy chuha! 🐭😱
Mummy sofa par chadh gayi, lekin tabhi toy chuha ghoom kar Kaartik ke pairo ke paas aa gaya! 😂
Dekhiye Kaartik ka prank kaise backfire hua!

Kya aapko bhi chuhe se darr lagta hai? Sach sach batana! 👇❤️

#shorts #TheNaughtyDuo #mouseprank #funnycartoon #3danimation #kartikandkaavya #comedy #familycomedy #relatable #viralshorts #cartoonhindi"""

# Locked to mROirKAfmE4 CoComelon 3D Standards
SCENES = [
    {
        "part": 1,
        "slot": 3,
        "email": "pinku.pub@gmail.com",
        "label": "Scene 1 - Kaartik Winds Up Toy Mouse",
        "prompt": (
            "Vertical 9:16 aspect ratio, 8 seconds. CoComelon meets Pixar 3D animated style for toddlers "
            "(gold standard: https://youtube.com/shorts/mROirKAfmE4). Full 3D CGI animation. "
            "Modern warm vibrant Indian living room. Beautiful 3D mother Pinki (25, powder-blue kurti) sits comfortably on sofa reading a colorful book. "
            "Adorable chubby 3D toddler Kaartik (5, yellow polo, rounded rosy cheeks, big glassy 3D brown eyes) sneaks up behind the sofa "
            "and winds up a cute tiny plastic gray toy mouse with red wheels, releasing it on the cozy carpet toward Mummy. "
            "Adorable 3D toddler Kaavya (3, pink frock, double buns) giggles quietly holding tiny hands over mouth. "
            "Smooth fluid 3D character motion, soft volumetric studio lighting, rich 3D subsurface scattering. "
            "STRICTLY NO 2D drawings, NO flat sketches, NO comic speech bubbles, NO text overlays."
        ),
        "outfile": RAW_CLIPS / "ep06_3d_p1.mp4"
    },
    {
        "part": 2,
        "slot": 5,
        "email": "elegantdriveways4u@gmail.com",
        "label": "Scene 2 - Mummy Hilarious Sofa Leap",
        "prompt": (
            "Vertical 9:16 aspect ratio, 8 seconds. CoComelon meets Pixar 3D animated style for toddlers "
            "(gold standard: https://youtube.com/shorts/mROirKAfmE4). Full 3D CGI animation. "
            "Modern Indian living room. The cute tiny toy mouse gently bumps into Mummy Pinki's slippers. "
            "Pinki looks down and comically freezes in wide-eyed cartoon shock, leaping hilariously right onto the sofa cushions clutching a soft yellow cushion! "
            "Chubby 3D toddler Kaartik (yellow polo) rolls on the carpet laughing with pure toddler joy, clapping his hands. "
            "Pixar 3D lighting, glossy realistic 3D hair and skin shaders, soft ambient occlusion, bright pastel colors. "
            "STRICTLY NO 2D cartoon, NO flat art, NO comic speech bubbles, NO written words."
        ),
        "outfile": RAW_CLIPS / "ep06_3d_p2.mp4"
    },
    {
        "part": 3,
        "slot": 6,
        "email": "abhiv446@gmail.com",
        "label": "Scene 3 - Mouse Turns Around & Climax Hug",
        "prompt": (
            "Vertical 9:16 aspect ratio, 8 seconds. CoComelon meets Pixar 3D animated style for toddlers "
            "(gold standard: https://youtube.com/shorts/mROirKAfmE4). Full 3D CGI animation. "
            "Modern sunlit Indian living room. The tiny toy mouse bounces off the sofa leg, turns around, and rolls straight toward Kaartik's bare feet! "
            "Kaartik's eyes pop open in funny toddler panic, leaping in comical slow motion straight onto the sofa clutching Mummy Pinki! "
            "Kaavya claps and giggles hysterically, and all three burst into uncontrollable happy family laughter and a big warm hug on the sofa. "
            "Adorable Pixar 3D emotional comedy climax, bright vibrant colors, volumetric glow. "
            "STRICTLY NO 2D drawings, NO pencil lines, NO comic text bubbles, NO flat illustrations."
        ),
        "outfile": RAW_CLIPS / "ep06_3d_p3.mp4"
    }
]

def setup_page_canvas(page, slot_idx, email):
    url = f"https://flow.google.com/u/{slot_idx}/"
    print(f"[*] [Slot {slot_idx} - {email}] Navigating to {url}...", flush=True)
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(3000)

    new_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i]").first
    if new_btn.count() > 0 and new_btn.is_visible():
        new_btn.click()
        page.wait_for_timeout(4000)

    print(f"[+] [Slot {slot_idx}] Canvas ready: {page.url}", flush=True)

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
            print(f"[!] [Slot {slot_idx}] Tune warning: {e}", flush=True)

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
                print(f"[+] [Slot {slot_idx}] Triggering 720p download -> {out_path.name}...", flush=True)
                with page.expect_download(timeout=60000) as dl_info:
                    target_720.click(force=True)
                dl = dl_info.value
                dl.save_as(str(out_path))
                print(f"[🏆 SAVED] [Slot {slot_idx} - Scene {part_num}]: {out_path.name} ({out_path.stat().st_size} bytes)", flush=True)
                return True
                
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
            print(f"[🏆 SAVED] [Slot {slot_idx} - Scene {part_num}]: {out_path.name} ({out_path.stat().st_size} bytes)", flush=True)
            return True
            
    print(f"[!] [Slot {slot_idx} - Scene {part_num}] Download failed to trigger.", flush=True)
    return False

def stitch_scenes(scene_files, final_output):
    print("\n" + "=" * 60, flush=True)
    print("  STITCHING 3D COCOMELON SCENES INTO MASTER SHORT", flush=True)
    print("=" * 60, flush=True)
    
    concat_list = BASE_DIR / "data" / "concat_3d_ep06.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for sf in scene_files:
            f.write(f"file '{sf.resolve()}'\n")
            
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
    
    print(f"[*] Running FFmpeg stitch...", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and final_output.exists() and final_output.stat().st_size > 0:
        print(f"[🎉 MASTERPIECE READY] {final_output.name} ({final_output.stat().st_size / (1024*1024):.2f} MB)", flush=True)
        verify_frame = BASE_DIR / "data" / "ep06_cocomelon_test_frame.png"
        subprocess.run([FFMPEG_BIN, "-y", "-ss", "00:00:03", "-i", str(final_output), "-vframes", "1", str(verify_frame)], capture_output=True)
        print(f"[📸 Verification Frame Saved]: {verify_frame}", flush=True)
        return True
    else:
        print(f"[!] FFmpeg stitch failed: {res.stderr}", flush=True)
        return False

def upload_short_via_studio(video_file, title, description):
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

        # Handle Skip if present
        skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
        if skip.count() > 0 and skip.is_visible():
            skip.click()
            page.wait_for_timeout(3000)

        # Click Create
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

        # File input
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

        print(f"[+] Attaching video file: {video_file}...", flush=True)
        file_input.set_input_files(str(video_file))
        page.wait_for_timeout(8000)

        # Video link capture
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

        # Set Title
        title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        if title_box.count() > 0:
            title_box.click()
            page.wait_for_timeout(300)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            title_box.fill(title[:100])
            page.wait_for_timeout(500)
            print("[+] Title set!", flush=True)

        # Set Description
        desc_box = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
        if desc_box.count() > 0:
            desc_box.click()
            page.wait_for_timeout(300)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            desc_box.fill(description)
            page.wait_for_timeout(500)
            print("[+] Description set!", flush=True)

        # Set Audience
        not_kids = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
        if not_kids.count() > 0:
            not_kids.click()
            page.wait_for_timeout(500)
            print("[+] Audience set: Not made for kids.", flush=True)

        # Wizard steps
        for step in range(3):
            next_btn = page.locator("ytcp-button#next-button, button:has-text('Next')").first
            if next_btn.count() > 0 and next_btn.is_visible() and next_btn.is_enabled():
                next_btn.click()
                print(f"[+] Clicked Next (Step {step+1})", flush=True)
                page.wait_for_timeout(2500)

        # Visibility: PUBLIC
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
            page.wait_for_timeout(3000)

        # Handle checks modal if any
        pub_anyway = page.locator("button:has-text('Publish anyway'), ytcp-button:has-text('Publish anyway')").first
        if pub_anyway.count() > 0 and pub_anyway.is_visible():
            print("[+] Clicking 'Publish anyway' modal...", flush=True)
            pub_anyway.click(force=True)
            page.wait_for_timeout(4000)

        # Final link check
        if not video_link:
            dialog_links = page.locator("ytcp-video-share-dialog a, a[href*='youtu.be']")
            if dialog_links.count() > 0:
                for i in range(dialog_links.count()):
                    href = dialog_links.nth(i).get_attribute("href")
                    if href and "youtu.be" in href:
                        video_link = href
                        break

        browser.close()

        if video_link:
            vid_id = video_link.split("/")[-1].split("?")[0]
            final_shorts_url = f"https://youtube.com/shorts/{vid_id}"
            print(f"[🎉 SUCCESS] YouTube Video Published: {final_shorts_url}", flush=True)
            return final_shorts_url
        return None

def main():
    print("=" * 70, flush=True)
    print("  THE NAUGHTY DUO — AUTONOMOUS HIGH-SPEED 3D ENGINE", flush=True)
    print(f"  Episode: {EPISODE_ID} | Benchmark: mROirKAfmE4 3D Locked", flush=True)
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
        for s in SCENES:
            page = ctx.new_page()
            setup_page_canvas(page, s["slot"], s["email"])
            active_sessions.append((page, s))

        # Submit prompts simultaneously
        print("\n" + "=" * 60, flush=True)
        print("  DISPATCHING ALL 3 COCOMELON 3D CGI PROMPTS SIMULTANEOUSLY", flush=True)
        print("=" * 60, flush=True)
        for page, s in active_sessions:
            submit_prompt_to_page(page, s["slot"], s["prompt"], s["part"])

        # Auto approvals
        for _ in range(5):
            time.sleep(1)
            for page, s in active_sessions:
                handle_approvals(page, s["slot"], s["part"])

        # Parallel monitoring
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

        # Download scenes
        print("\n" + "=" * 60, flush=True)
        print("  DOWNLOADING HIGH-FIDELITY 3D CGI SCENES", flush=True)
        print("=" * 60, flush=True)
        downloaded = []
        for page, s in active_sessions:
            success = download_video_clip(page, s["slot"], s["part"], s["outfile"])
            if success and s["outfile"].exists():
                downloaded.append(s["outfile"])

        ctx.close()

    if len(downloaded) == 3:
        final_mp4 = OUTPUT_DIR / f"{EPISODE_ID}_final.mp4"
        if stitch_scenes(downloaded, final_mp4):
            live_url = upload_short_via_studio(final_mp4, TITLE, DESCRIPTION)
            if live_url:
                # Update uploaded log
                import json
                log_file = r"C:\TheNaughtyDuo_Automation\uploaded_videos_log.json"
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    data.setdefault("uploaded", []).append({
                        "key": EPISODE_ID,
                        "filename": f"{EPISODE_ID}_final.mp4",
                        "size_mb": round(final_mp4.stat().st_size / (1024 * 1024), 2),
                        "youtube": live_url,
                        "youtube_title": TITLE,
                        "visual_style": "100% 3D CGI CoComelon & Pixar (mROirKAfmE4 Lock)",
                        "youtube_status": "LIVE",
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    with open(log_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    print("[✓] Updated uploaded_videos_log.json!", flush=True)
                except Exception as e:
                    print(f"[!] Log update warning: {e}", flush=True)
                print(f"\n[🏆 FULL CYCLE COMPLETED] LIVE URL: {live_url}", flush=True)
    else:
        print(f"[!] Only {len(downloaded)}/3 scenes downloaded successfully.", flush=True)

if __name__ == "__main__":
    main()
