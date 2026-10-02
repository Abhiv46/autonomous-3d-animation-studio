import os
import sys
import time
import subprocess
import json
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
    "Vertical 9:16 aspect ratio, 8 seconds. CoComelon meets Pixar 3D animated style for toddlers "
    "(gold standard: https://youtube.com/shorts/mROirKAfmE4). Full 3D CGI animation. "
    "Modern warm vibrant Indian living room. Beautiful 3D mother (25, powder-blue kurti) sits comfortably on sofa reading a colorful book. "
    "Adorable chubby 3D toddler boy Kaartik (5, yellow polo, rounded rosy cheeks, big glassy 3D brown eyes) sneaks up behind the sofa "
    "and winds up a cute tiny plastic gray toy mouse with red wheels, releasing it on the cozy carpet. "
    "Adorable 3D toddler girl Kaavya (3, pink frock, double buns) giggles quietly holding tiny hands over mouth. "
    "Smooth fluid 3D character motion, soft volumetric studio lighting, rich 3D subsurface scattering. "
    "STRICTLY NO 2D drawings, NO flat sketches, NO comic speech bubbles, NO text overlays."
)
OUT_FILE = RAW_CLIPS / "ep06_3d_p1.mp4"

TITLE = "Ghar Me Aaya Nakli Chuha! 🐭😱 Kaartik Ka Prank Backfire! #TheNaughtyDuo #shorts"
DESCRIPTION = """Kaartik ne Mummy ko darane ke liye chhoda nakli toy chuha! 🐭😱
Mummy sofa par chadh gayi, lekin tabhi toy chuha ghoom kar Kaartik ke pairo ke paas aa gaya! 😂
Dekhiye Kaartik ka prank kaise backfire hua!

Kya aapko bhi chuhe se darr lagta hai? Sach sach batana! 👇❤️

#shorts #TheNaughtyDuo #mouseprank #funnycartoon #3danimation #kartikandkaavya #comedy #familycomedy #relatable #viralshorts #cartoonhindi"""

def generate_and_download_scene1():
    print("=" * 60, flush=True)
    print(f"  GENERATING EPISODE 06 SCENE 1 ON SLOT {SLOT} ({EMAIL})", flush=True)
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

        new_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i]").first
        if new_btn.count() > 0 and new_btn.is_visible():
            new_btn.click()
            page.wait_for_timeout(4000)

        print(f"[+] Canvas ready: {page.url}", flush=True)

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

        print("[*] Waiting for Veo render (~75s)...", flush=True)
        start_time = time.time()
        for i in range(1, 22):
            time.sleep(5)
            elapsed = int(time.time() - start_time)
            stop_btn = page.locator("button:has-text('Stop'), button[aria-label='Stop']")
            is_rendering = stop_btn.count() > 0 and stop_btn.first.is_visible()
            vids = page.locator("video, [aria-label*='Open video in editor' i]").count()
            print(f"[{elapsed}s] Slot {SLOT}: {'Render' if is_rendering else 'Ready'} ({vids} vids)", flush=True)
            if not is_rendering and vids > 0 and elapsed >= 30:
                print(f"[+] Render ready after {elapsed}s!", flush=True)
                break

        print("[*] Attempting download for Scene 1...", flush=True)
        cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video")
        download_success = False
        if cards.count() > 0:
            cards.last.click(force=True)
            page.wait_for_timeout(3000)
            
            # Wait if rendering percentage is visible in player
            for _ in range(10):
                txt = page.locator("body").inner_text()
                if any(f"{p}%" in txt for p in range(1, 100)):
                    print("[*] Still finishing rendering in player, waiting 4s...", flush=True)
                    page.wait_for_timeout(4000)
                else:
                    break
            
            dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
            if dl_btn.count() > 0 and dl_btn.is_visible():
                dl_btn.click(force=True)
                page.wait_for_timeout(1500)
                
                target_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size')").first
                if target_720.count() > 0:
                    print(f"[+] Triggering 720p download -> {OUT_FILE.name}...", flush=True)
                    with page.expect_download(timeout=60000) as dl_info:
                        target_720.click(force=True)
                    dl = dl_info.value
                    dl.save_as(str(OUT_FILE))
                    print(f"[SAVED] Scene 1: {OUT_FILE.name} ({OUT_FILE.stat().st_size} bytes)", flush=True)
                    download_success = True

        ctx.close()
        return download_success

def stitch_masterpiece():
    p1 = RAW_CLIPS / "ep06_3d_p1.mp4"
    p2 = RAW_CLIPS / "ep06_3d_p2.mp4"
    p3 = RAW_CLIPS / "ep06_3d_p3.mp4"

    if not (p1.exists() and p2.exists() and p3.exists()):
        print(f"[!] Missing parts: p1={p1.exists()}, p2={p2.exists()}, p3={p3.exists()}", flush=True)
        return None

    final_output = OUTPUT_DIR / "ep_06_toy_mouse_final.mp4"
    concat_list = BASE_DIR / "data" / "concat_3d_ep06.txt"
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

    print(f"[*] Stitching Episode 06 with FFmpeg...", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and final_output.exists() and final_output.stat().st_size > 0:
        print(f"[🎉 MASTERPIECE READY] {final_output.name} ({final_output.stat().st_size / (1024*1024):.2f} MB)", flush=True)
        verify_frame = BASE_DIR / "data" / "ep06_cocomelon_test_frame.png"
        subprocess.run([FFMPEG_BIN, "-y", "-ss", "00:00:03", "-i", str(final_output), "-vframes", "1", str(verify_frame)], capture_output=True)
        return final_output
    else:
        print(f"[!] Stitch failed: {res.stderr}", flush=True)
        return None

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
            print("[!] File input not found.", flush=True)
            browser.close()
            return None

        print(f"[+] Attaching video file: {video_file}...", flush=True)
        file_input.set_input_files(str(video_file))
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

        title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        if title_box.count() > 0:
            title_box.click()
            page.wait_for_timeout(300)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            title_box.fill(title[:100])
            page.wait_for_timeout(500)
            print("[+] Title set!", flush=True)

        desc_box = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
        if desc_box.count() > 0:
            desc_box.click()
            page.wait_for_timeout(300)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            desc_box.fill(description)
            page.wait_for_timeout(500)
            print("[+] Description set!", flush=True)

        not_kids = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
        if not_kids.count() > 0:
            not_kids.click()
            page.wait_for_timeout(500)
            print("[+] Audience set: Not made for kids.", flush=True)

        for step in range(3):
            next_btn = page.locator("ytcp-button#next-button, button:has-text('Next')").first
            if next_btn.count() > 0 and next_btn.is_visible() and next_btn.is_enabled():
                next_btn.click()
                print(f"[+] Clicked Next (Step {step+1})", flush=True)
                page.wait_for_timeout(2500)

        pub_radio = page.locator("ytcp-uploads-dialog tp-yt-paper-radio-button[name='PUBLIC'], tp-yt-paper-radio-button[name='PUBLIC']").first
        if pub_radio.count() > 0:
            pub_radio.click(force=True)
            print("[+] Visibility set: PUBLIC.", flush=True)
            page.wait_for_timeout(1500)

        publish_btn = page.locator("ytcp-uploads-dialog ytcp-button#done-button, ytcp-uploads-dialog button:has-text('Publish'), ytcp-uploads-dialog #publish-button").first
        if publish_btn.count() == 0:
            publish_btn = page.locator("button:has-text('Publish')").first
        if publish_btn.count() > 0:
            publish_btn.click(force=True)
            print("[+] Clicked Publish!", flush=True)
            page.wait_for_timeout(3000)

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

        if video_link:
            vid_id = video_link.split("/")[-1].split("?")[0]
            final_shorts_url = f"https://youtube.com/shorts/{vid_id}"
            print(f"[🎉 SUCCESS] YouTube Video Published: {final_shorts_url}", flush=True)
            return final_shorts_url
        return None

if __name__ == "__main__":
    if generate_and_download_scene1():
        final_video = stitch_masterpiece()
        if final_video:
            live_url = upload_short_via_studio(final_video, TITLE, DESCRIPTION)
            if live_url:
                log_file = r"C:\TheNaughtyDuo_Automation\uploaded_videos_log.json"
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    data.setdefault("uploaded", []).append({
                        "key": "ep_06_toy_mouse",
                        "filename": "ep_06_toy_mouse_final.mp4",
                        "size_mb": round(final_video.stat().st_size / (1024 * 1024), 2),
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
                    print(f"[!] Log warning: {e}", flush=True)
                print(f"\n[🏆 FULL CYCLE COMPLETED] LIVE URL: {live_url}", flush=True)
