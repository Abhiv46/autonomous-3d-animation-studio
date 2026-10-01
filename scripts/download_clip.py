import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
raw_clips = BASE_DIR / "data" / "raw_clips"
raw_clips.mkdir(parents=True, exist_ok=True)

brave_exe = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
brave_data = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=brave_data,
        executable_path=brave_exe,
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    url = "https://flow.google.com/u/3/project/a1c6f19b-b046-41f3-9b33-fbc756646163"
    page = ctx.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(6000)
    
    # Click first tile to enter video timeline editor
    tile = page.locator("flow-grid-tile-container").first
    print("Clicking first video tile...")
    tile.click(force=True)
    page.wait_for_timeout(2000)
    
    # Find the download button (aria-label='Download media')
    dl_btn = page.locator("button[aria-label='Download media']").first
    print("Found download media button, clicking...")
    dl_btn.click(force=True)
    page.wait_for_timeout(1000)
    page.screenshot(path=str(BASE_DIR / "data" / "download_menu_open.png"))
    
    # Check menu options (e.g. 720p, 1080p, Video, etc.)
    options = page.locator("[role='menuitem'], mat-menu-item, button").all()
    print("Download menu options:", len(options))
    target_dl = None
    for opt in options:
        txt = opt.inner_text().strip()
        print(f"Option: '{txt}'")
        if any(res in txt.lower() for res in ["720p", "1080p", "mp4", "download video", "original"]):
            target_dl = opt
            break
            
    if not target_dl and len(options) > 0:
        target_dl = options[0]
        
    if target_dl:
        out_video_path = raw_clips / "ep_18_scene_01.mp4"
        print(f"Triggering download to {out_video_path}...")
        try:
            with page.expect_download(timeout=30000) as dl_info:
                target_dl.click(force=True)
            dl = dl_info.value
            dl.save_as(str(out_video_path))
            print(f"SUCCESS: Video downloaded to {out_video_path} (Size: {out_video_path.stat().st_size} bytes)")
        except Exception as e:
            print(f"Download trigger error: {e}")

    ctx.close()
