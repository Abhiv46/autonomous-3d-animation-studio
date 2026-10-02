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

SCENE3_STORY = (
    "Seamless continuous scene climax. Cozy warm domestic bedroom. High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. Full 3D CGI animation. "
    "Beautiful Indian mother Pinki (25, traditional powder-blue kurti, dark hair braid) rushes into the bedroom holding a laundry basket. "
    "Suddenly she freezes with wide comical shocked eyes as the flying cockroach buzzes past her nose! "
    "Pinki comically tosses the laundry basket into the air with an exaggerated cartoon scream, and leaps dramatically onto the bed! "
    "She cuddles chubby toddler Kaartik (5, yellow polo) and cute toddler Kaavya (3.5, pink pajamas, double hair buns) safely under the fluffy duvet blanket. "
    "All three peek out nervously together from under the duvet, holding up slippers and giggling in adorable heartwarming family comedy relief! "
    "Ultra-detailed Pixar 3D CGI animation, comical cartoon physics, warm cozy bedroom lighting, soft background bokeh. "
    "STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays."
)

FULL_PROMPT = f"{STYLE_BLOCK}\n\n{SCENE3_STORY}\n\n{AVOID_BLOCK}"

def generate_scene3():
    print("=" * 65)
    print("  LAUNCHING SCENE 3 GENERATION IN 'THE NAUGHTY DUO' (SLOT 0)")
    print("  CHARACTER REFERENCES: Pinki + kaavya + kaartik")
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

        # Ensure we are on the canvas (close any open video editor)
        back_btn = page.locator("button[aria-label*='back' i]").first
        if back_btn.count() > 0 and back_btn.is_visible():
            back_btn.click(force=True)
            page.wait_for_timeout(2000)

        # Attach Pinki
        add_btn = page.locator("button[aria-label='Add ingredients to the prompt box']").first
        if add_btn.count() > 0:
            print("[*] Attaching 'Pinki' character reference...")
            add_btn.click(force=True)
            page.wait_for_timeout(2000)
            overlay = page.locator(".cdk-overlay-pane, mat-dialog-container, [role='dialog']").first
            if overlay.count() > 0:
                p_opt = overlay.locator("text='Pinki'").first
                if p_opt.count() > 0:
                    p_opt.click(force=True)
                    page.wait_for_timeout(1000)
                    overlay.locator("button:has-text('Add to prompt')").first.click(force=True)
                    page.wait_for_timeout(1000)

        # Attach Kaavya
        if add_btn.count() > 0:
            print("[*] Attaching 'kaavya' character reference...")
            add_btn.click(force=True)
            page.wait_for_timeout(2000)
            overlay = page.locator(".cdk-overlay-pane, mat-dialog-container, [role='dialog']").first
            if overlay.count() > 0:
                kv_opt = overlay.locator("text='kaavya'").first
                if kv_opt.count() > 0:
                    kv_opt.click(force=True)
                    page.wait_for_timeout(1000)
                    overlay.locator("button:has-text('Add to prompt')").first.click(force=True)
                    page.wait_for_timeout(1000)

        # Attach Kaartik
        if add_btn.count() > 0:
            print("[*] Attaching 'kaartik' character reference...")
            add_btn.click(force=True)
            page.wait_for_timeout(2000)
            overlay = page.locator(".cdk-overlay-pane, mat-dialog-container, [role='dialog']").first
            if overlay.count() > 0:
                kt_opt = overlay.locator("text='kaartik'").first
                if kt_opt.count() > 0:
                    kt_opt.click(force=True)
                    page.wait_for_timeout(1000)
                    overlay.locator("button:has-text('Add to prompt')").first.click(force=True)
                    page.wait_for_timeout(1000)

        # Enter Scene 3 Prompt
        print("[*] Entering locked Scene 3 prompt...")
        editor = page.locator(".ProseMirror").first
        editor.click()
        editor.fill(FULL_PROMPT)
        page.wait_for_timeout(1000)

        # Submit Scene 3
        print("[*] Submitting Scene 3 generation...")
        gen_btn = page.locator("button[aria-label='Start generation']").first
        if gen_btn.count() > 0 and gen_btn.is_enabled():
            gen_btn.click(force=True)
        else:
            page.keyboard.press("Control+Enter")

        page.wait_for_timeout(4000)

        # Approve if dialog appears
        approve_btn = page.locator("button:has-text('Approve'), div:has-text('Approve'), span:has-text('Approve')").first
        if approve_btn.count() > 0 and approve_btn.is_visible():
            print("[+] Approving Scene 3 generation...")
            approve_btn.click(force=True)
            page.wait_for_timeout(3000)

        # Check render progress
        for check in range(6):
            page.wait_for_timeout(5000)
            stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
            print(f"  Check {check+1}: Render stop count = {stop_btn.count()}")
            if stop_btn.count() > 0:
                print("[🚀 CONFIRMED] Scene 3 generation has actively begun!")
                break

        page.screenshot(path="data/tnd_scene3_progress.png")
        browser.close()
        print("[+] Scene 3 submission complete.")

if __name__ == "__main__":
    generate_scene3()
