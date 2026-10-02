import os
import sys
import time
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
OUTPUT_DIR = BASE_DIR / "data" / "output"
RAW_CLIPS.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

DOWNLOAD_TARGETS = [
    {
        "part": 1,
        "url": "https://flow.google.com/u/4/project/6e1e0d92-cb51-42fc-9b78-c88c25588a90",
        "out_file": RAW_CLIPS / "ep_18_scene_01.mp4"
    },
    {
        "part": 2,
        "url": "https://flow.google.com/u/5/project/f108b2ea-5cd9-4935-bc7d-fb28af947fbb",
        "out_file": RAW_CLIPS / "ep_18_scene_02.mp4"
    },
    {
        "part": 3,
        "url": "https://flow.google.com/u/6/project/ae61f63b-63d9-4a3c-b8f3-9439de42dc87",
        "out_file": RAW_CLIPS / "ep_18_scene_03.mp4"
    }
]

def download_rendered_clip(page, target):
    part = target["part"]
    url = target["url"]
    out_path = target["out_file"]
    
    print(f"\n[*] [Scene {part}] Navigating to {url}...", flush=True)
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(4000)
    
    # Click video tile or open in editor
    card = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video").first
    if card.count() > 0:
        card.click(force=True)
        page.wait_for_timeout(2500)
        
        # Click download
        dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
        if dl_btn.count() > 0 and dl_btn.is_visible():
            dl_btn.click(force=True)
            page.wait_for_timeout(1000)
            
            # Select 720p or MP4
            opt = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size')").first
            if opt.count() > 0:
                print(f"[+] [Scene {part}] Triggering download to {out_path}...", flush=True)
                with page.expect_download(timeout=60000) as dl_info:
                    opt.click(force=True)
                dl = dl_info.value
                dl.save_as(str(out_path))
                print(f"[🏆] [Scene {part}] SAVED: {out_path.name} ({out_path.stat().st_size} bytes)", flush=True)
                return True
                
    # Fallback: check direct download button on page
    dl_direct = page.locator("button[aria-label='Download media'], button[aria-label*='download' i]").first
    if dl_direct.count() > 0 and dl_direct.is_visible():
        dl_direct.click(force=True)
        page.wait_for_timeout(1000)
        opt = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p')").first
        if opt.count() > 0:
            with page.expect_download(timeout=60000) as dl_info:
                opt.click(force=True)
            dl = dl_info.value
            dl.save_as(str(out_path))
            print(f"[🏆] [Scene {part}] SAVED: {out_path.name} ({out_path.stat().st_size} bytes)", flush=True)
            return True
            
    print(f"[!] [Scene {part}] Could not trigger download directly, taking screenshot...", flush=True)
    page.screenshot(path=str(BASE_DIR / "data" / f"scene_{part}_dl_error.png"))
    return False

def main():
    print("=" * 60, flush=True)
    print("  DOWNLOADING 3 PARALLEL RENDERED SCENES (SLOTS 4, 5, 6)", flush=True)
    print("=" * 60, flush=True)

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            accept_downloads=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = ctx.new_page()
        for t in DOWNLOAD_TARGETS:
            download_rendered_clip(page, t)
        ctx.close()

if __name__ == "__main__":
    main()
