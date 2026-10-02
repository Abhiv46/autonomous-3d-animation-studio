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

PROJECT_URL = "https://flow.google.com/u/0/project/1876f0f7-bc42-4764-86c9-35d76cb3a615"
BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
S2_CLIP = RAW_CLIPS / "ep20_arm_wrestling_p2.mp4"
S2_FRAME = RAW_CLIPS / "ep20_arm_wrestling_p2_sample.png"

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
FFMPEG_BIN = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

STYLE_BLOCK = (
    "Semi-realistic 3D animated style, Pixar/Disney-inspired rendering with soft painterly texture, "
    "warm cinematic color grading. Vibrant lighting, rich subsurface skin scattering, fluid cartoon character animation."
)
AVOID_BLOCK = "Avoid: flat 2D look, inconsistent facial features, extra fingers, distorted hands, blurry background, style shifting mid-scene, anatomy errors, redesigned character"

SCENE2_PROMPT = f"""{STYLE_BLOCK}

Seamless continuous scene climax. Warm domestic dining room, golden morning sunlight. High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. Full 3D CGI animation.
Big bearded loving father (white henley t-shirt) opens his mouth in an exaggerated comical shocked cartoon expression, pretending tiny toddler daughter Kaavya has superhuman Hulk strength! 
Papa pretends to struggle, sweat bead on his brow, as his giant arm slowly bends backward toward the rustic dining table! 
Kaavya (3.5 years old, double hair buns with pink scrunchies, pink pajamas) pushes with adorable victorious giggles!
SLAP! Papa's giant hand gently hits the wooden table in defeat! 
Kaavya leaps up raising both tiny arms in the air cheering with pure uncontainable joy like a champion! 
Papa laughs warmly with pure fatherly love, scooping tiny Kaavya up high onto his broad shoulders! Kaartik (5 years old, yellow polo) claps enthusiastically in the background!
Ultra-detailed Pixar 3D rendering, fluid cartoon slapstick animation, glowing warm lighting.
STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays.

{AVOID_BLOCK}"""

def generate_and_download_s2():
    print("=" * 65)
    print("  GENERATING SCENE 2 (THE VICTORY MOMENT) IN TND")
    print("=" * 65)

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

        page.goto(PROJECT_URL, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)

        # Make sure canvas is shown
        back_btn = page.locator("button[aria-label*='back' i]").first
        if back_btn.count() > 0 and back_btn.is_visible():
            back_btn.click(force=True)
            page.wait_for_timeout(2000)

        # Attach Kaavya
        add_btn = page.locator("button[aria-label='Add ingredients to the prompt box']").first
        if add_btn.count() > 0:
            print("[*] Attaching 'kaavya' asset...")
            add_btn.click(force=True)
            page.wait_for_timeout(1500)
            overlay = page.locator(".cdk-overlay-pane, [role='dialog']").first
            if overlay.count() > 0:
                k_opt = overlay.locator("text='kaavya'").first
                if k_opt.count() > 0:
                    k_opt.click(force=True)
                    page.wait_for_timeout(1000)
                    overlay.locator("button:has-text('Add to prompt')").first.click(force=True)
                    page.wait_for_timeout(1000)

        # Attach Kaartik
        if add_btn.count() > 0:
            print("[*] Attaching 'kaartik' asset...")
            add_btn.click(force=True)
            page.wait_for_timeout(1500)
            overlay = page.locator(".cdk-overlay-pane, [role='dialog']").first
            if overlay.count() > 0:
                kt_opt = overlay.locator("text='kaartik'").first
                if kt_opt.count() > 0:
                    kt_opt.click(force=True)
                    page.wait_for_timeout(1000)
                    overlay.locator("button:has-text('Add to prompt')").first.click(force=True)
                    page.wait_for_timeout(1000)

        # Fill prompt
        print("[*] Entering Scene 2 prompt...")
        editor = page.locator(".ProseMirror").first
        editor.click()
        editor.fill(SCENE2_PROMPT)
        page.wait_for_timeout(1000)

        # Submit
        print("[*] Submitting Scene 2...")
        gen_btn = page.locator("button[aria-label='Start generation']").first
        if gen_btn.count() > 0 and gen_btn.is_enabled():
            gen_btn.click(force=True)
        else:
            page.keyboard.press("Control+Enter")

        page.wait_for_timeout(4000)

        # Approve
        approve_btn = page.locator("button:has-text('Approve'), div:has-text('Approve'), span:has-text('Approve')").first
        if approve_btn.count() > 0 and approve_btn.is_visible():
            print("[+] Approving Scene 2...")
            approve_btn.click(force=True)
            page.wait_for_timeout(3000)

        # Monitor render to complete
        print("[*] Waiting for Scene 2 render to finish...")
        for check in range(16):
            page.wait_for_timeout(5000)
            stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
            print(f"  Check {check+1}: Stop button count = {stop_btn.count()}")
            if check > 3 and stop_btn.count() == 0:
                print("[+] Scene 2 render completed!")
                break

        # Return to canvas
        back_btn = page.locator("button[aria-label*='back' i]").first
        if back_btn.count() > 0 and back_btn.is_visible():
            back_btn.click(force=True)
            page.wait_for_timeout(2000)

        # Click newest tile (Tile 0)
        tiles = page.locator("flow-grid-tile-container, div.flow-grid-tile, [aria-label*='video' i]").all()
        print(f"[*] Found {len(tiles)} tiles. Clicking Tile 0 (Scene 2)...")
        tiles[0].click(force=True)
        page.wait_for_timeout(2500)

        # Download
        dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
        if dl_btn.count() > 0:
            dl_btn.click(force=True)
            page.wait_for_timeout(1500)
            target = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size'), button:has-text('1080p')").first
            if target.count() > 0:
                with page.expect_download(timeout=60000) as dl_info:
                    target.click(force=True)
                dl = dl_info.value
                dl.save_as(str(S2_CLIP))
                print(f"[🏆 DOWNLOAD COMPLETE]: {S2_CLIP.name} ({S2_CLIP.stat().st_size} bytes)")

                subprocess.run([
                    FFMPEG_BIN, "-y",
                    "-ss", "00:00:03",
                    "-i", str(S2_CLIP),
                    "-vframes", "1",
                    "-q:v", "2",
                    str(S2_FRAME)
                ], capture_output=True)

        browser.close()

if __name__ == "__main__":
    generate_and_download_s2()
