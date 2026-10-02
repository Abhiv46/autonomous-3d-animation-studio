import os
import sys
import time
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

# Ensure UTF-8 output on Windows
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
P1_OUT = RAW_CLIPS / f"{EPISODE_ID}_p1.mp4"

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

def run_scene1_production():
    print("=" * 65, flush=True)
    print(f"[*] Starting Ep 15 Scene 1 on Slot {SLOT_IDX} ({SLOT_EMAIL})...", flush=True)
    print("=" * 65, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            accept_downloads=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        print(f"[*] Opening Slot {SLOT_IDX} Flow...", flush=True)
        page.goto(f"https://flow.google.com/u/{SLOT_IDX}/", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)

        # Click New Project
        new_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i]").first
        if new_btn.count() > 0 and new_btn.is_visible():
            print("[+] Clicking New project...", flush=True)
            new_btn.click()
            page.wait_for_timeout(5000)

        print(f"[*] Project Canvas URL: {page.url}", flush=True)

        # Enter prompt
        editor = page.locator("div.ProseMirror").first
        if editor.count() == 0:
            print("[-] Could not find div.ProseMirror!", flush=True)
            browser.close()
            return False

        editor.click(force=True)
        page.wait_for_timeout(400)
        editor.fill(P1_PROMPT)
        print("[+] Prompt filled into editor.", flush=True)
        page.wait_for_timeout(1000)

        start_btn = page.locator("button[aria-label*='Start generation' i]").first
        if start_btn.count() > 0:
            print("[+] Clicking Start generation button...", flush=True)
            start_btn.click(force=True)
        else:
            print("[+] Pressing Enter...", flush=True)
            page.keyboard.press("Enter")

        page.wait_for_timeout(2000)

        # Approve credits
        for _ in range(5):
            app = page.locator("button:has-text('Always approve'), button:has-text('Approve')")
            if app.count() > 0 and app.last.is_visible():
                print(f"[+] Approved: {app.last.inner_text()}", flush=True)
                app.last.click(force=True)
                page.wait_for_timeout(1000)
                break
            time.sleep(1)

        print("[*] Prompt submitted! Waiting for render to finish (~70-90s)...", flush=True)

        # Keep browser open and poll every 8 seconds
        for elapsed in range(15):
            time.sleep(8)
            stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
            dots = page.locator("div.chat-bubble-ellipsis, .pulsing-dots")
            print(f"[*] Elapsed: ~{(elapsed+1)*8}s | Stop btn: {stop_btn.count()}", flush=True)

            if elapsed >= 8 and stop_btn.count() == 0:
                print("[+] Generation completed! Looking for video card...", flush=True)
                break

        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_scene1_render_finished.png")

        # Now download video
        cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video")
        print(f"[*] Found {cards.count()} video elements/cards", flush=True)

        if cards.count() > 0:
            cards.last.click(force=True)
            page.wait_for_timeout(2500)

            dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
            if dl_btn.count() > 0 and dl_btn.is_visible():
                dl_btn.click(force=True)
                page.wait_for_timeout(1500)

                target_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size')").first
                if target_720.count() > 0:
                    print(f"[+] Downloading 720p to {P1_OUT.name}...", flush=True)
                    with page.expect_download(timeout=60000) as dl_info:
                        target_720.click(force=True)
                    dl = dl_info.value
                    dl.save_as(str(P1_OUT))
                    print(f"[SUCCESS] Scene 1 downloaded: {P1_OUT.name} ({P1_OUT.stat().st_size} bytes)", flush=True)
                    browser.close()
                    return True

        browser.close()
        return False

if __name__ == "__main__":
    run_scene1_production()
