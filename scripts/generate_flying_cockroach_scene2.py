import os
import sys
import time
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
BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

STYLE_BLOCK = (
    "Semi-realistic 3D animated style, Pixar/Disney-inspired rendering with soft painterly texture, "
    "warm cinematic color grading. Vibrant lighting, rich subsurface skin scattering, fluid cartoon character animation."
)
AVOID_BLOCK = "Avoid: flat 2D look, inconsistent facial features, extra fingers, distorted hands, blurry background, style shifting mid-scene, anatomy errors, redesigned character"

SCENE2_STORY = (
    "Seamless continuous scene. Cozy domestic bedroom, warm golden lamp glow. "
    "High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. Full 3D CGI animation. "
    "Cute chubby toddler girl Kaavya (3.5 years old, double hair buns with pink scrunchies, pink pajamas) "
    "stands on the wooden stool about to strike. Suddenly, the shiny cockroach opens its glossy translucent wings and buzzes up flying directly into the air toward the camera! "
    "Kaavya's eyes go cartoonishly huge in comical shock, she screams silently, drops the pink slipper, and leaps off the stool into the arms of toddler brother Kaartik (5 years old, yellow polo shirt). "
    "Both chubby toddlers tumble backward comically onto the soft rug in hilarious exaggerated slapstick panic, pointing upward in shock! "
    "Ultra-fluid 3D character animation, comical cartoon physics, rich subsurface scattering, vibrant warm studio lighting. "
    "STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays."
)

FULL_PROMPT = f"{STYLE_BLOCK}\n\n{SCENE2_STORY}\n\n{AVOID_BLOCK}"

def generate_scene2():
    print("=" * 65)
    print("  LAUNCHING SCENE 2 GENERATION IN 'THE NAUGHTY DUO' (SLOT 0)")
    print("  STORY: THE WINGS OPEN & FLYING COCKROACH PANIC!")
    print("=" * 65)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        print(f"[*] Navigating to {PROJECT_URL}...")
        page.goto(PROJECT_URL, wait_until="domcontentloaded", timeout=40000)
        page.wait_for_timeout(4000)

        # Exit any editor view if active
        done_btn = page.locator("button:has-text('Done')").first
        if done_btn.count() > 0 and done_btn.is_visible():
            print("[+] Clicking Done to return to canvas...")
            done_btn.click()
            page.wait_for_timeout(2000)

        # Step 1: Attach Kaavya
        add_btn = page.locator("button[aria-label='Add ingredients to the prompt box']").first
        if add_btn.count() > 0:
            print("[*] Clicking Add ingredients button...")
            add_btn.click(force=True)
            page.wait_for_timeout(2000)

            # In the popup overlay, select kaavya
            overlay = page.locator(".cdk-overlay-pane, mat-dialog-container, [role='dialog']").first
            if overlay.count() > 0:
                k_opt = overlay.locator("text='kaavya'").first
                if k_opt.count() > 0:
                    k_opt.click(force=True)
                    page.wait_for_timeout(1000)
                    add_to_prompt = overlay.locator("button:has-text('Add to prompt')").first
                    if add_to_prompt.count() > 0:
                        add_to_prompt.click(force=True)
                        print("[+] Attached 'kaavya' character chip!")
                        page.wait_for_timeout(1000)

        # Step 2: Attach Kaartik
        if add_btn.count() > 0:
            add_btn.click(force=True)
            page.wait_for_timeout(2000)
            overlay = page.locator(".cdk-overlay-pane, mat-dialog-container, [role='dialog']").first
            if overlay.count() > 0:
                k2_opt = overlay.locator("text='kaartik'").first
                if k2_opt.count() > 0:
                    k2_opt.click(force=True)
                    page.wait_for_timeout(1000)
                    add_to_prompt = overlay.locator("button:has-text('Add to prompt')").first
                    if add_to_prompt.count() > 0:
                        add_to_prompt.click(force=True)
                        print("[+] Attached 'kaartik' character chip!")
                        page.wait_for_timeout(1000)

        # Step 3: Enter prompt
        print("[*] Entering locked Scene 2 prompt...")
        editor = page.locator(".ProseMirror").first
        editor.click()
        editor.fill(FULL_PROMPT)
        page.wait_for_timeout(1000)

        # Step 4: Submit prompt
        print("[*] Submitting Scene 2 prompt...")
        gen_btn = page.locator("button[aria-label='Start generation']").first
        if gen_btn.count() > 0 and gen_btn.is_enabled():
            gen_btn.click(force=True)
        else:
            page.keyboard.press("Control+Enter")

        page.wait_for_timeout(4000)

        # Step 5: Check approval dialog
        approve_btn = page.locator("button:has-text('Approve'), div:has-text('Approve'), span:has-text('Approve')").first
        if approve_btn.count() > 0 and approve_btn.is_visible():
            print("[+] Approval dialog detected! Clicking Approve...")
            approve_btn.click(force=True)
            page.wait_for_timeout(3000)

        # Monitor generation start
        print("[*] Monitoring Scene 2 render progress...")
        for check in range(6):
            page.wait_for_timeout(5000)
            stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
            print(f"  Check {check+1}: Active render stop button count = {stop_btn.count()}")
            if stop_btn.count() > 0:
                print("[🚀 CONFIRMED] Scene 2 generation has actively begun on Google Flow!")
                break

        page.screenshot(path="data/tnd_scene2_progress.png")
        browser.close()
        print("[+] Scene 2 submission complete.")

if __name__ == "__main__":
    generate_scene2()
