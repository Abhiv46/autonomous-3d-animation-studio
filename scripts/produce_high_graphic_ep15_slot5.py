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
P2_TEST = RAW_CLIPS / "ep_15_scene2_high_graphic.mp4"
P2_SAMPLE = RAW_CLIPS / "ep_15_scene2_high_graphic_sample.png"

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
FFMPEG_BIN = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

SLOT_URL = "https://flow.google.com/u/5/"

# Carefully crafted prompt matching Scene 1's exact toddler proportions, camera language, and vibrant Pixar CGI
SCENE_2_PROMPT = (
    "High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. "
    "Full 3D CGI animation. Bright sunlit modern kitchen of Indian home, warm morning sunlight. "
    "Toddler eye-level dynamic camera tracking shot. "
    "Chubby 3D toddler boy Kaartik (5 years old, bright yellow polo shirt with small chest pocket, cuffed blue denim shorts, "
    "round blushing chubby cheeks, dark messy toddler hair fringe, cute drawn black handlebar moustache on his upper lip). "
    "He stands proudly on a small wooden step stool at the kitchen marble counter, pointing his giant red plastic magnifying glass "
    "at a large glass jar of chocolate chip cookies with a determined, funny serious cop face. "
    "Beside him, cute 3D toddler sister Kaavya (3.5 years old, bright pink cotton dress, double hair buns with pink ties) "
    "jumps excitedly on the kitchen floor, enthusiastically saluting with a wooden cooking spoon and giggling. "
    "Vibrant Pixar 3D lighting, crisp subsurface skin scattering, fluid natural cartoon character animation, ultra-detailed textures. "
    "STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays."
)

def run():
    print("=" * 65, flush=True)
    print("  GENERATING HIGH-GRAPHIC SCENE 2 ON SLOT 5 (elegantdriveways4u@gmail.com)", flush=True)
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

        print(f"[*] Navigating to Slot 5: {SLOT_URL}...", flush=True)
        page.goto(SLOT_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        # Click New project
        new_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i], div:has-text('New project')").first
        if new_btn.count() > 0 and new_btn.is_visible():
            print("[+] Clicking New project...", flush=True)
            new_btn.click(force=True)
            page.wait_for_timeout(5000)

        print(f"[*] Canvas URL: {page.url}", flush=True)

        editor = page.locator("div.ProseMirror").first
        if editor.count() == 0:
            print("[-] Editor not found!", flush=True)
            browser.close()
            return

        editor.click(force=True)
        page.wait_for_timeout(300)
        editor.fill(SCENE_2_PROMPT)
        page.wait_for_timeout(1000)

        start_btn = page.locator("button[aria-label*='Start generation' i]").first
        if start_btn.count() > 0:
            start_btn.click(force=True)
        else:
            page.keyboard.press("Enter")

        print("[*] Prompt submitted. Checking approval dialog...", flush=True)
        for _ in range(20):
            opt = page.locator("div.option-row:has-text('Always approve'), span.option-label:has-text('Always approve'), div.option-row:has-text('Approve'), button:has-text('Always approve'), button:has-text('Approve')").first
            if opt.count() > 0 and opt.is_visible():
                box = opt.bounding_box()
                if box:
                    page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                else:
                    opt.click(force=True)
                print("[+] Clicked Approval!", flush=True)
                break
            time.sleep(2)

        page.screenshot(path=str(BASE_DIR / "data" / "debug_slot5_s2_submitted.png"))

        print("[*] Waiting for video render (~70-90s)...", flush=True)
        time.sleep(60)

        for _ in range(16):
            stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
            if stop_btn.count() == 0:
                print("[+] Render finished or no stop button!", flush=True)
                break
            time.sleep(5)

        page.screenshot(path=str(BASE_DIR / "data" / "debug_slot5_s2_rendered.png"))

        # Download 720p
        cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video")
        if cards.count() > 0:
            print(f"[+] Found {cards.count()} video elements. Clicking latest...", flush=True)
            cards.first.click(force=True)
            page.wait_for_timeout(2500)
            dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
            if dl_btn.count() > 0 and dl_btn.is_visible():
                dl_btn.click(force=True)
                page.wait_for_timeout(1500)
                target_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size')").first
                if target_720.count() > 0:
                    print(f"[+] Downloading 720p to {P2_TEST.name}...", flush=True)
                    with page.expect_download(timeout=60000) as dl_info:
                        target_720.click(force=True)
                    dl = dl_info.value
                    dl.save_as(str(P2_TEST))
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(1000)

                    if P2_TEST.exists() and P2_TEST.stat().st_size > 1000000:
                        print(f"[🏆 SAVED]: {P2_TEST.name} ({P2_TEST.stat().st_size} bytes)", flush=True)
                        # Extract sample frame for visual inspection
                        subprocess.run([FFMPEG_BIN, "-y", "-ss", "00:00:03", "-i", str(P2_TEST), "-vframes", "1", str(P2_SAMPLE)], capture_output=True)
                        print(f"[📸 Sample Frame Extracted]: {P2_SAMPLE.name}", flush=True)

        browser.close()

if __name__ == "__main__":
    run()
