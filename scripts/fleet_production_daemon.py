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
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from scripts.tiktok_studio_uploader import upload_to_tiktok_studio
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
OUTPUT_DIR = BASE_DIR / "data" / "output"
RAW_CLIPS.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
FFMPEG_BIN = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
UPLOAD_LOG = Path(r"C:\TheNaughtyDuo_Automation\uploaded_videos_log.json")
SLATE_JSON = BASE_DIR / "data" / "next_viral_production_slate.json"
STATUS_FILE = BASE_DIR / "data" / "live_production_status.json"

ACTIVE_SLOTS = [
    {"slot": 7, "email": "rkumar.ukb@gmail.com"},
    {"slot": 5, "email": "elegantdriveways4u@gmail.com"},
    {"slot": 6, "email": "abhiv446@gmail.com"},
    {"slot": 4, "email": "infolillylooks@gmail.com"},
    {"slot": 0, "email": "TecHWirE9999@gmail.com"}
]

def update_live_status(ep_id, title, account_str, scene_str, pct, stage_str):
    status_data = {
        "active_id": ep_id,
        "active_title": title,
        "active_account": account_str,
        "active_scene": scene_str,
        "percentage": pct,
        "parts_text": f"{pct}% Progress | Fleet Operations Daemon Active",
        "stage": stage_str,
        "target_platform": "YouTube Shorts (Auto-Publish)",
        "delay_reason": f"🟢 Running: {stage_str}"
    }
    try:
        STATUS_FILE.write_text(json.dumps(status_data, indent=2), encoding="utf-8")
    except Exception:
        pass

def extract_last_frame(input_video, output_image):
    cmd = [
        FFMPEG_BIN, "-y",
        "-sseof", "-0.1",
        "-i", str(input_video),
        "-update", "1",
        "-q:v", "1",
        str(output_image)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0 and output_image.exists()

def attach_anchor_frame(page, image_path):
    print(f"[*] Attaching Frame Anchor: {image_path.name}...", flush=True)
    plus_btn = page.locator("[aria-label*='Add ingredients' i]").last
    if plus_btn.count() == 0:
        plus_btn = page.locator("button:has-text('add')").last
    plus_btn.click()
    page.wait_for_timeout(1000)

    with page.expect_file_chooser() as fc_info:
        up_btn = page.locator("button:has-text('Upload media')").first
        if up_btn.count() == 0:
            up_btn = page.locator("div:has-text('Upload media')").first
        up_btn.click(force=True)

    fc = fc_info.value
    fc.set_files(str(image_path))
    page.wait_for_timeout(5000)

    add_to_prompt = page.locator("button:has-text('Add to prompt'), [role='button']:has-text('Add to prompt')").first
    if add_to_prompt.count() > 0:
        add_to_prompt.click(force=True)
        page.wait_for_timeout(1500)
        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)
        print(f"[✓ Anchor Attached]: {image_path.name}", flush=True)
        return True
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
        except Exception:
            pass

def handle_approvals(page):
    for _ in range(3):
        target = page.locator("button:has-text('Always approve'), [role='button']:has-text('Always approve')")
        if target.count() > 0 and target.last.is_visible():
            target.last.click(force=True)
            page.wait_for_timeout(1000)
            return
        app_target = page.locator("button:has-text('Approve'), [role='button']:has-text('Approve')")
        if app_target.count() > 0 and app_target.last.is_visible():
            app_target.last.click(force=True)
            page.wait_for_timeout(1000)
            return
        time.sleep(1)

def wait_and_download_video(page, p_num, out_path, timeout_secs=120):
    print(f"[*] [Scene {p_num}] Waiting for render (~60-90s)...", flush=True)
    start_time = time.time()
    time.sleep(60)
    while time.time() - start_time < timeout_secs:
        handle_approvals(page)
        cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video")
        if cards.count() > 0:
            progress = page.locator("mat-progress-bar, [role='progressbar'], .loading-spinner")
            if progress.count() == 0 or not progress.first.is_visible():
                print(f"[✓] [Scene {p_num}] Render appears complete after {int(time.time() - start_time)}s!", flush=True)
                break
        time.sleep(5)

    for attempt in range(4):
        print(f"[*] [Scene {p_num}] Download attempt {attempt+1}...", flush=True)
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
                    print(f"[+] [Scene {p_num}] Downloading 720p to {out_path.name}...", flush=True)
                    try:
                        with page.expect_download(timeout=60000) as dl_info:
                            target_720.click(force=True)
                        dl = dl_info.value
                        dl.save_as(str(out_path))
                        page.keyboard.press("Escape")
                        page.wait_for_timeout(1000)
                        if out_path.exists() and out_path.stat().st_size > 1000000:
                            print(f"[🏆 SAVED] Scene {p_num}: {out_path.name} ({out_path.stat().st_size} bytes)", flush=True)
                            return True
                    except Exception as e:
                        print(f"[!] Download attempt error: {e}", flush=True)
        # Direct download fallback
        dl_direct = page.locator("button[aria-label='Download media'], button[aria-label*='download' i]").first
        if dl_direct.count() > 0 and dl_direct.is_visible():
            dl_direct.click(force=True)
            page.wait_for_timeout(1000)
            target_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p')").first
            if target_720.count() > 0:
                try:
                    with page.expect_download(timeout=60000) as dl_info:
                        target_720.click(force=True)
                    dl = dl_info.value
                    dl.save_as(str(out_path))
                    if out_path.exists() and out_path.stat().st_size > 1000000:
                        return True
                except Exception:
                    pass
        time.sleep(10)
    return False

def stitch_and_export(clips, output_path):
    concat_txt = BASE_DIR / "data" / "concat_temp_slate.txt"
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

def upload_to_youtube_with_seo(video_file, title, description, tags):
    print(f"\n[*] Uploading {video_file.name} to YouTube Shorts...", flush=True)
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
        time.sleep(4)

        skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
        if skip.count() > 0 and skip.is_visible():
            skip.click()
            page.wait_for_timeout(3000)

        create_btn = page.locator("ytcp-button#create-icon, button:has-text('Create'), ytcp-button:has-text('Create')").first
        if create_btn.count() > 0:
            create_btn.click()
            page.wait_for_timeout(1500)
            upload_option = page.get_by_text("Upload videos", exact=False).first
            if upload_option.count() > 0:
                upload_option.click()
            page.wait_for_timeout(2000)

        file_input = page.locator("input[type='file']").first
        if file_input.count() == 0:
            browser.close()
            return None

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

        # Title
        title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        if title_box.count() > 0:
            title_box.click()
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            title_box.fill(title[:100])
            page.wait_for_timeout(500)

        # Description
        desc_box = page.locator("#description-textarea div#textbox, ytcp-mention-textbox#description-textarea div#textbox").first
        if desc_box.count() == 0:
            tbs = page.locator("#textbox")
            if tbs.count() >= 2:
                desc_box = tbs.nth(1)
        if desc_box.count() > 0:
            desc_box.click()
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            desc_box.fill(description)
            page.wait_for_timeout(500)

        # Audience: Not made for kids
        not_kids = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
        if not_kids.count() > 0:
            not_kids.click()
            page.wait_for_timeout(500)

        # Show more for tags
        show_more = page.locator("#toggle-button, button:has-text('Show more')").first
        if show_more.count() > 0 and show_more.is_visible():
            show_more.click()
            page.wait_for_timeout(1000)

        tags_input = page.locator("#tags-container input, input[aria-label='Tags'], #text-input").first
        if tags_input.count() > 0:
            tags_input.click()
            for t in tags:
                page.keyboard.type(t)
                page.keyboard.press("Enter")
                time.sleep(0.05)

        for _ in range(3):
            next_btn = page.locator("ytcp-button#next-button, button:has-text('Next')").first
            if next_btn.count() > 0 and next_btn.is_visible() and next_btn.is_enabled():
                next_btn.click()
                page.wait_for_timeout(2500)

        pub_radio = page.locator("ytcp-uploads-dialog tp-yt-paper-radio-button[name='PUBLIC'], tp-yt-paper-radio-button[name='PUBLIC']").first
        if pub_radio.count() > 0:
            pub_radio.click(force=True)
            page.wait_for_timeout(1500)

        publish_btn = page.locator("ytcp-uploads-dialog ytcp-button#done-button, ytcp-uploads-dialog button:has-text('Publish'), ytcp-uploads-dialog #publish-button").first
        if publish_btn.count() > 0:
            publish_btn.click(force=True)
            page.wait_for_timeout(4000)

        pub_anyway = page.locator("button:has-text('Publish anyway'), ytcp-button:has-text('Publish anyway')").first
        if pub_anyway.count() > 0 and pub_anyway.is_visible():
            pub_anyway.click(force=True)
            page.wait_for_timeout(4000)

        browser.close()
        return video_link

def sync_published_log(ep_id, title, filepath, yt_url, tiktok_caption=None, tiktok_posted=False):
    entry = {
        "key": ep_id,
        "filename": filepath.name,
        "size_mb": round(filepath.stat().st_size / (1024 * 1024), 2),
        "youtube": yt_url,
        "youtube_title": title,
        "visual_style": "High-Definition Pixar 3D CGI (100% Chained)",
        "youtube_status": "LIVE" if yt_url else "FAILED",
        "tiktok": "posted" if tiktok_posted else "pending",
        "tiktok_caption": tiktok_caption,
        "tiktok_timestamp": time.strftime("%Y-%m-%d %H:%M:%S") if tiktok_posted else None,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        data = json.loads(UPLOAD_LOG.read_text(encoding="utf-8")) if UPLOAD_LOG.exists() else {"uploaded": []}
        data.setdefault("uploaded", []).append(entry)
        UPLOAD_LOG.write_text(json.dumps(data, indent=4), encoding="utf-8")
    except Exception as e:
        print(f"[!] Log sync warning: {e}")

def run_slate_production():
    print("=" * 70, flush=True)
    print("  FLEET OPERATIONS DAEMON — VIRAL PRODUCTION SLATE EXECUTION", flush=True)
    print("=" * 70, flush=True)

    slate_data = json.loads(SLATE_JSON.read_text(encoding="utf-8"))
    episodes = slate_data.get("production_slate", [])

    slot_cycle = 0

    for ep in episodes:
        ep_id = ep["episode_id"]
        title = ep["title"]
        desc = ep["seo_metadata"]["description"]
        tags = ep["seo_metadata"]["tags"]
        scenes = ep["scenes"]

        master_out = OUTPUT_DIR / f"{ep_id}_master.mp4"
        if master_out.exists() and master_out.stat().st_size > 1000000:
            print(f"[✓] Episode {ep_id} already exists on disk. Skipping.", flush=True)
            continue

        assigned = ACTIVE_SLOTS[slot_cycle % len(ACTIVE_SLOTS)]
        slot_cycle += 1
        s_num = assigned["slot"]
        s_email = assigned["email"]

        print(f"\n[🚀 STARTING] {ep_id}: {title} on Slot {s_num} ({s_email})", flush=True)
        update_live_status(ep_id, title, f"/u/{s_num}/ ({s_email})", "Starting Scene 1 of 3", 10, "Setting up Project Canvas")

        rendered_clips = []
        anchor_path = None

        with sync_playwright() as p:
            ctx = p.chromium.launch_persistent_context(
                user_data_dir=BRAVE_DATA,
                executable_path=BRAVE_EXE,
                headless=True,
                accept_downloads=True,
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = ctx.new_page()
            page.goto(f"https://flow.google.com/u/{s_num}/", wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(3000)

            new_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i]").first
            if new_btn.count() > 0 and new_btn.is_visible():
                new_btn.click()
                page.wait_for_timeout(4000)

            configure_tune(page)

            for sc_idx, sc in enumerate(scenes):
                p_num = sc["scene_index"]
                p_prompt = sc["veo_prompt"]
                p_out = RAW_CLIPS / f"{ep_id}_p{p_num}.mp4"
                p_last = RAW_CLIPS / f"{ep_id}_p{p_num}_last.png"

                pct = 20 + (sc_idx * 25)
                update_live_status(ep_id, title, f"/u/{s_num}/ ({s_email})", f"Generating Scene {p_num} of 3", pct, f"Rendering Scene {p_num} in Google Flow")

                if p_out.exists() and p_out.stat().st_size > 1000000:
                    print(f"[✓ Reusing Scene {p_num}]: {p_out.name}", flush=True)
                    rendered_clips.append(p_out)
                    anchor_path = p_last
                    continue

                if anchor_path and anchor_path.exists():
                    attach_anchor_frame(page, anchor_path)

                editor = page.locator("[contenteditable='true'], div.ProseMirror, textarea").first
                editor.click()
                editor.fill(p_prompt)
                page.wait_for_timeout(500)

                send_btn = page.locator("button:has-text('arrow_forward'), button[aria-label*='Submit' i]").first
                if send_btn.count() > 0 and send_btn.is_visible():
                    send_btn.click()
                else:
                    page.keyboard.press("Enter")

                print(f"[🚀 SENT] Scene {p_num} prompt dispatched to Slot {s_num}!", flush=True)
                page.wait_for_timeout(2000)
                handle_approvals(page)

                sc_ok = wait_and_download_video(page, p_num, p_out)

                if sc_ok:
                    print(f"[✓ Scene {p_num} SAVED]: {p_out.name} ({p_out.stat().st_size} bytes)", flush=True)
                    rendered_clips.append(p_out)
                    extract_last_frame(p_out, p_last)
                    anchor_path = p_last
                else:
                    print(f"[!] Scene {p_num} failed on Slot {s_num}.", flush=True)
                    break

            ctx.close()

        if len(rendered_clips) == 3:
            update_live_status(ep_id, title, f"/u/{s_num}/ ({s_email})", "Stitching Master Short", 85, "FFmpeg High-Definition Stitching")
            stitch_ok = stitch_and_export(rendered_clips, master_out)
            if stitch_ok:
                update_live_status(ep_id, title, f"/u/{s_num}/ ({s_email})", "Publishing to YouTube", 90, "Uploading with Full Viral SEO to YouTube")
                yt_link = upload_to_youtube_with_seo(master_out, title, desc, tags)

                # Clean Title & Viral TikTok Caption with Full SEO
                clean_title = title.split("#")[0].strip()
                tt_caption = f"{clean_title} #TheNaughtyDuo #shorts #viral #funny #comedy #3danimation #hindicartoon #foryou #fyp #trending"
                
                update_live_status(ep_id, title, f"/u/{s_num}/ ({s_email})", "Publishing to TikTok", 95, "Uploading with Full Viral SEO to TikTok Studio")
                tt_ok = upload_to_tiktok_studio(str(master_out), tt_caption)

                if yt_link or tt_ok:
                    print(f"\n[🎉 PUBLISHED DUAL]: YT: {yt_link} | TikTok: {'LIVE' if tt_ok else 'FAILED'}", flush=True)
                    sync_published_log(ep_id, title, master_out, yt_link, tiktok_caption=tt_caption, tiktok_posted=tt_ok)
                    update_live_status(ep_id, title, f"/u/{s_num}/ ({s_email})", "Completed & Live", 100, f"Published Dual: YT ({yt_link}) & TikTok ({'Live' if tt_ok else 'Pending'})")
        else:
            print(f"[!] Incomplete scenes for {ep_id}.", flush=True)

    print("\n[✓ ENTIRE VIRAL SLATE FINISHED]", flush=True)

if __name__ == "__main__":
    run_slate_production()
