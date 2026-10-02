import os
import sys
import time
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
OUTPUT_DIR = BASE_DIR / "data" / "output"
FFMPEG_BIN = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

PROJECT_URL = "https://flow.google.com/u/7/project/22978ea9-4a73-48dd-afd3-271e93176f0a"
OUT_FILE = RAW_CLIPS / "ep18_3d_p1.mp4"

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
    print(f"[*] Opening project {PROJECT_URL}...", flush=True)
    page.goto(PROJECT_URL, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(4000)

    # Check rendering percentage
    for i in range(15):
        txt = page.locator("body").inner_text()
        has_pct = any(f"{p}%" in txt for p in range(1, 100))
        if has_pct:
            print(f"[*] Still rendering... waiting 5s (iter {i+1})...", flush=True)
            page.wait_for_timeout(5000)
        else:
            print("[+] Render complete or ready to download!", flush=True)
            break

    # Look for download button
    dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download'), button:has([data-icon*='download' i])").first
    if dl_btn.count() == 0:
        # Check download icon at top
        dl_btn = page.locator("button:has(svg), [role='button']").filter(has=page.locator("path[d*='M19 9h-4V3H9v6H5l7 7 7-7z'], path[d*='download' i]")).first
    if dl_btn.count() == 0:
        # Check standard toolbar icons
        dl_btn = page.locator("button[aria-label='Download'], button[title='Download']").first

    print(f"[*] dl_btn count: {dl_btn.count()}", flush=True)
    if dl_btn.count() > 0:
        dl_btn.click(force=True)
        page.wait_for_timeout(1500)
        opt = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size')").first
        if opt.count() > 0:
            print(f"[+] Clicking 720p download -> {OUT_FILE}...", flush=True)
            with page.expect_download(timeout=60000) as dl_info:
                opt.click(force=True)
            dl = dl_info.value
            dl.save_as(str(OUT_FILE))
            print(f"[🏆] SAVED Scene 1: {OUT_FILE.name} ({OUT_FILE.stat().st_size} bytes)", flush=True)
        else:
            print("[!] 720p option not found, trying direct download...", flush=True)
    else:
        # Click the video card to open editor if in canvas
        card = page.locator("[aria-label*='Open video in editor' i], video").first
        if card.count() > 0:
            card.click(force=True)
            page.wait_for_timeout(3000)
            dl_btn2 = page.locator("button[aria-label*='Download' i]").first
            if dl_btn2.count() > 0:
                dl_btn2.click(force=True)
                page.wait_for_timeout(1500)
                opt = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p')").first
                if opt.count() > 0:
                    with page.expect_download(timeout=60000) as dl_info:
                        opt.click(force=True)
                    dl = dl_info.value
                    dl.save_as(str(OUT_FILE))
                    print(f"[🏆] SAVED Scene 1: {OUT_FILE.name} ({OUT_FILE.stat().st_size} bytes)", flush=True)

    page.screenshot(path=str(BASE_DIR / "data" / "slot7_check.png"))
    ctx.close()

# If downloaded, stitch!
p1 = RAW_CLIPS / "ep18_3d_p1.mp4"
p2 = RAW_CLIPS / "ep18_3d_p2.mp4"
p3 = RAW_CLIPS / "ep18_3d_p3.mp4"
if p1.exists() and p2.exists() and p3.exists():
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
