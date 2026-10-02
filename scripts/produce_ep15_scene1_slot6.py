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

SLOT_IDX = 6
SLOT_EMAIL = "abhiv446@gmail.com"

EPISODE_ID = "ep_15_fake_moustache_cop"
P1_FILE = RAW_CLIPS / f"{EPISODE_ID}_p1.mp4"
P1_LAST = RAW_CLIPS / f"{EPISODE_ID}_p1_last.png"

P1_PROMPT = (
    "Vertical 9:16 aspect ratio, 8 seconds. CoComelon meets Pixar 3D animated style for toddlers "
    "(gold standard: https://youtube.com/shorts/mROirKAfmE4). Full 3D CGI animation, ultra-adorable rounded "
    "chubby toddler character models, oversized cute heads, rosy blushing cheeks, big expressive glassy 3D brown eyes, "
    "volumetric 3D hair with glossy highlights, soft glowing peach skin with gentle subsurface scattering, bright pastel studio lighting, soft ambient occlusion. "
    "Camera starts in extreme macro close-up on Kaartik (5 years old, yellow polo) who has an oversized black drawn handlebar moustache on his face. "
    "He blows a toy whistle with puffed cheeks, scowling comically like a tough cop. Camera zooms back rapidly to reveal him marching with heavy slow steps into a "
    "bright colorful modern kitchen holding a giant red plastic magnifying glass. Behind him, Kaavya (3 years old, pink frock, double buns) waddles excitedly wearing "
    "a shiny foil badge and saluting with a wooden cooking spatula. "
    "STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO comic speech bubbles, NO text overlays. "
    "(All character voices, exclamations and spoken dialogue must strictly be in cheerful HINDI language matching the Hindi title. No English speech)."
)

def configure_tune(page):
    tune_btn = page.locator("button:has-text('tune'), [aria-label*='settings' i], [aria-label*='tune' i], [aria-label='Settings']").last
    if tune_btn.count() > 0 and tune_btn.is_visible():
        try:
            tune_btn.click()
            page.wait_for_timeout(1000)
            never_radio = page.locator("span:has-text('Never'), [role='radio']:has-text('Never'), div:has-text('Never')").last
            if never_radio.count() > 0:
                never_radio.click(force=True)
                page.wait_for_timeout(500)
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)
            print("[+] Configured Tune settings.", flush=True)
        except Exception:
            page.keyboard.press("Escape")

def handle_approvals(page):
    for _ in range(4):
        target = page.locator("button:has-text('Always approve'), [role='button']:has-text('Always approve')")
        if target.count() > 0 and target.last.is_visible():
            target.last.click(force=True)
            print("[✓ Approved]: Always approve clicked!", flush=True)
            page.wait_for_timeout(1000)
            return True
        app_target = page.locator("button:has-text('Approve'), [role='button']:has-text('Approve')")
        if app_target.count() > 0 and app_target.last.is_visible():
            app_target.last.click(force=True)
            print("[✓ Approved]: Approve clicked!", flush=True)
            page.wait_for_timeout(1000)
            return True
        time.sleep(1)
    return False

def generate_scene1():
    print("=" * 65, flush=True)
    print(f"  GENERATING EPISODE 15 SCENE 1 ON SLOT {SLOT_IDX} ({SLOT_EMAIL})", flush=True)
    print("=" * 65, flush=True)

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
        page.set_viewport_size({"width": 1600, "height": 1000})

        print(f"[*] Navigating to Google Flow Slot {SLOT_IDX}...", flush=True)
        page.goto(f"https://flow.google.com/u/{SLOT_IDX}/", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)

        # Click New Project
        new_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i], div:has-text('New project')").first
        if new_btn.count() > 0 and new_btn.is_visible():
            print("[+] Clicking New Project...", flush=True)
            new_btn.click()
            page.wait_for_timeout(5000)

        print(f"[*] Project Canvas URL: {page.url}", flush=True)
        configure_tune(page)

        # Enter Prompt
        editor = page.locator("div.ProseMirror, [contenteditable='true']").first
        if editor.count() == 0:
            print("[!] Could not locate div.ProseMirror!", flush=True)
            ctx.close()
            return False

        print("[*] Entering Scene 1 prompt...", flush=True)
        editor.click()
        page.wait_for_timeout(500)
        editor.fill(P1_PROMPT)
        page.wait_for_timeout(1000)

        # Click Start generation button
        start_btn = page.locator("button[aria-label*='Start generation' i], button:has-text('arrow_forward')").last
        if start_btn.count() > 0 and start_btn.is_visible():
            print("[+] Clicking Start Generation button...", flush=True)
            start_btn.click(force=True)
        else:
            print("[+] Triggering via Enter key...", flush=True)
            page.keyboard.press("Enter")

        page.wait_for_timeout(2000)
        handle_approvals(page)

        # Wait for video generation (~65s to 90s)
        print("[*] Waiting for video generation (~65s to 90s)...", flush=True)
        start_time = time.time()
        time.sleep(60)

        for _ in range(15):
            handle_approvals(page)
            cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video")
            if cards.count() > 0:
                progress = page.locator("mat-progress-bar, [role='progressbar'], .loading-spinner")
                if progress.count() == 0 or not progress.first.is_visible():
                    print(f"[✓] Render appears complete after {int(time.time() - start_time)}s!", flush=True)
                    break
            time.sleep(5)

        # Download video
        downloaded = False
        for attempt in range(4):
            print(f"[*] Download attempt {attempt+1}...", flush=True)
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
                        print(f"[+] Downloading 720p to {P1_FILE.name}...", flush=True)
                        try:
                            with page.expect_download(timeout=60000) as dl_info:
                                target_720.click(force=True)
                            dl = dl_info.value
                            dl.save_as(str(P1_FILE))
                            page.keyboard.press("Escape")
                            page.wait_for_timeout(1000)
                            if P1_FILE.exists() and P1_FILE.stat().st_size > 1000000:
                                print(f"[🏆 SAVED] Scene 1: {P1_FILE.name} ({P1_FILE.stat().st_size} bytes)", flush=True)
                                downloaded = True
                                break
                        except Exception as e:
                            print(f"[!] Download attempt error: {e}", flush=True)
            time.sleep(5)

        ctx.close()
        return downloaded

if __name__ == "__main__":
    generate_scene1()
