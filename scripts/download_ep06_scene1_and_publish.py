import os
import sys
import time
import shutil
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

PROJECT_URL = "https://flow.google.com/u/7/project/1fc9aac7-9ac6-4acf-a657-38bac6ecfe6c"
OUT_FILE = RAW_CLIPS / "ep06_3d_p1.mp4"

TITLE = "Ghar Me Aaya Nakli Chuha! 🐭😱 Kaartik Ka Prank Backfire! #TheNaughtyDuo #shorts"
DESCRIPTION = """Kaartik ne Mummy ko darane ke liye chhoda nakli toy chuha! 🐭😱
Mummy sofa par chadh gayi, lekin tabhi toy chuha ghoom kar Kaartik ke pairo ke paas aa gaya! 😂
Dekhiye Kaartik ka prank kaise backfire hua!

Kya aapko bhi chuhe se darr lagta hai? Sach sach batana! 👇❤️

#shorts #TheNaughtyDuo #mouseprank #funnycartoon #3danimation #kartikandkaavya #comedy #familycomedy #relatable #viralshorts #cartoonhindi"""

def download_rendered_clip():
    print(f"[*] Opening rendered project: {PROJECT_URL}...", flush=True)
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
        page.goto(PROJECT_URL, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)

        card = page.locator("[aria-label*='Open video in editor' i], video, flow-grid-tile-container").first
        if card.count() > 0:
            card.click(force=True)
            page.wait_for_timeout(3000)

        dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
        if dl_btn.count() > 0:
            dl_btn.click(force=True)
            page.wait_for_timeout(1500)
            target_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size')").first
            if target_720.count() > 0:
                print(f"[+] Clicking 720p download -> {OUT_FILE.name}...", flush=True)
                with page.expect_download(timeout=60000) as dl_info:
                    target_720.click(force=True)
                dl = dl_info.value
                tmp = dl.path()
                if tmp and os.path.exists(tmp):
                    shutil.copy2(tmp, str(OUT_FILE))
                else:
                    dl.save_as(str(OUT_FILE))
                print(f"[🏆 SAVED] Scene 1: {OUT_FILE.name} ({OUT_FILE.stat().st_size} bytes)", flush=True)
                ctx.close()
                return True

        ctx.close()
        return False

def stitch_and_upload():
    p1 = RAW_CLIPS / "ep06_3d_p1.mp4"
    p2 = RAW_CLIPS / "ep06_3d_p2.mp4"
    p3 = RAW_CLIPS / "ep06_3d_p3.mp4"

    if not (p1.exists() and p2.exists() and p3.exists()):
        print(f"[!] Parts missing: p1={p1.exists()}, p2={p2.exists()}, p3={p3.exists()}", flush=True)
        return False

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

    print(f"[*] Running FFmpeg stitch...", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and final_output.exists() and final_output.stat().st_size > 0:
        print(f"[🎉 MASTERPIECE READY] {final_output.name} ({final_output.stat().st_size / (1024*1024):.2f} MB)", flush=True)
        # Extract verification frame
        verify_frame = BASE_DIR / "data" / "ep06_cocomelon_test_frame.png"
        subprocess.run([FFMPEG_BIN, "-y", "-ss", "00:00:03", "-i", str(final_output), "-vframes", "1", str(verify_frame)], capture_output=True)

        # Upload
        print("\n[*] Starting YouTube Upload...", flush=True)
        with sync_playwright() as p:
            b = p.chromium.launch_persistent_context(
                user_data_dir=BRAVE_DATA,
                executable_path=BRAVE_EXE,
                headless=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = b.new_page()
            page.set_viewport_size({"width": 1600, "height": 1000})
            page.goto("https://studio.youtube.com", wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(4000)

            skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
            if skip.count() > 0 and skip.is_visible():
                skip.click()
                page.wait_for_timeout(3000)

            create_btn = page.locator("ytcp-button#create-icon, button:has-text('Create')").first
            if create_btn.count() > 0:
                create_btn.click()
                page.wait_for_timeout(1500)
                page.locator("text='Upload videos'").first.click()
                page.wait_for_timeout(2000)

            file_input = page.locator("input[type='file']").first
            file_input.set_input_files(str(final_output))
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

            # Details
            tb = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
            if tb.count() > 0:
                tb.click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                tb.fill(TITLE[:100])
                page.wait_for_timeout(500)

            db = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
            if db.count() > 0:
                db.click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                db.fill(DESCRIPTION)
                page.wait_for_timeout(500)

            nk = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
            if nk.count() > 0:
                nk.click()
                page.wait_for_timeout(500)

            for step in range(3):
                nxt = page.locator("ytcp-button#next-button, button:has-text('Next')").first
                if nxt.count() > 0 and nxt.is_enabled():
                    nxt.click()
                    page.wait_for_timeout(2000)

            # Public
            pub = page.locator("ytcp-uploads-dialog tp-yt-paper-radio-button[name='PUBLIC'], tp-yt-paper-radio-button[name='PUBLIC']").first
            if pub.count() > 0:
                pub.click(force=True)
                page.wait_for_timeout(1000)

            pub_btn = page.locator("ytcp-uploads-dialog ytcp-button#done-button, ytcp-uploads-dialog button:has-text('Publish'), ytcp-uploads-dialog #publish-button").first
            if pub_btn.count() == 0:
                pub_btn = page.locator("button:has-text('Publish')").first
            if pub_btn.count() > 0:
                pub_btn.click(force=True)
                page.wait_for_timeout(3000)

            pub_anyway = page.locator("button:has-text('Publish anyway'), ytcp-button:has-text('Publish anyway')").first
            if pub_anyway.count() > 0 and pub_anyway.is_visible():
                pub_anyway.click(force=True)
                page.wait_for_timeout(3000)

            b.close()

            if video_link:
                vid_id = video_link.split("/")[-1].split("?")[0]
                final_shorts_url = f"https://youtube.com/shorts/{vid_id}"
                print(f"[🎉 PUBLISHED LIVE] {final_shorts_url}", flush=True)

                # Record in uploaded log
                log_file = r"C:\TheNaughtyDuo_Automation\uploaded_videos_log.json"
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    data.setdefault("uploaded", []).append({
                        "key": "ep_06_toy_mouse",
                        "filename": "ep_06_toy_mouse_final.mp4",
                        "size_mb": round(final_output.stat().st_size / (1024 * 1024), 2),
                        "youtube": final_shorts_url,
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

                return final_shorts_url

    return None

if __name__ == "__main__":
    if download_rendered_clip():
        stitch_and_upload()
