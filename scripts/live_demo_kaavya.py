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
BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

# Master Style Block
STYLE_BLOCK = (
    "Semi-realistic 3D animated style, Pixar/Disney-inspired rendering with soft painterly texture, "
    "warm cinematic color grading. Vibrant lighting, rich subsurface skin scattering, fluid cartoon character animation."
)
AVOID_BLOCK = "Avoid: flat 2D look, inconsistent facial features, extra fingers, distorted hands, blurry background, style shifting mid-scene, anatomy errors, redesigned character"

KAAVYA_SOLO_PROMPT = f"""{STYLE_BLOCK}

Cozy sunlit living room with warm morning light streaming across a soft knitted carpet. High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. Full 3D CGI animation.
Adorable chubby toddler Kaavya (3.5 years old, cute double hair buns with pink scrunchies, rosy blushed cheeks, sweet pink cotton pajamas, sparkling large brown Disney eyes) decides to wear Papa's gigantic brown leather sneakers!
Her tiny feet are completely buried inside the oversized giant shoes. She takes slow, clumsy, adorable wobbly steps forward, holding both tiny chubby arms out sideways like airplane wings to keep balance!
She wobbles playfully, glances up at the camera with a cute innocent wide-eyed smile, and bursts into sweet joyous toddler giggles as she successfully takes three big steps!
Ultra-detailed textures: soft cotton pajamas, detailed leather on big shoes, soft carpet fibers, glowing skin subsurface scattering, cinematic shallow depth of field.
STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays.

{AVOID_BLOCK}"""

def run_visible_kaavya_session():
    print("\n" + "=" * 65)
    print("  LAUNCHING VISIBLE BRAVE BROWSER FOR LIVE KAAVYA GENERATION")
    print("=" * 65)

    with sync_playwright() as p:
        # Launching with headless=False so it opens visibly on user's monitor!
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--window-position=50,50",
                "--window-size=1600,950"
            ]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1500, "height": 900})

        print("\n[Step 1] Opening Flow and navigating into project 'The Naughty Duo'...")
        page.goto(PROJECT_URL, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(5000)

        # Close any open card/viewer if present
        back_btn = page.locator("button:has-text('Done'), button[aria-label*='back' i]").first
        if back_btn.count() > 0 and back_btn.is_visible():
            print("[*] Returning to canvas view...")
            back_btn.click(force=True)
            page.wait_for_timeout(2000)

        print("\n[Step 2] Attaching Kaavya character reference from ingredient library...")
        add_btn = page.locator("button[aria-label='Add ingredients to the prompt box']").first
        if add_btn.count() > 0 and add_btn.is_visible():
            add_btn.click(force=True)
            page.wait_for_timeout(2000)
            overlay = page.locator(".cdk-overlay-pane, [role='dialog']").first
            if overlay.count() > 0:
                kaavya_opt = overlay.locator("text='kaavya'").first
                if kaavya_opt.count() > 0:
                    print("[+] Selecting 'kaavya' character asset...")
                    kaavya_opt.click(force=True)
                    page.wait_for_timeout(1000)
                    add_to_prompt = overlay.locator("button:has-text('Add to prompt')").first
                    if add_to_prompt.count() > 0:
                        add_to_prompt.click(force=True)
                        print("[✓] 'kaavya' ingredient successfully added to prompt box!")
                        page.wait_for_timeout(1500)

        print("\n[Step 3] Setting and typing detailed Pixar 3D prompt into prompt box...")
        editor = page.locator(".ProseMirror").first
        if editor.count() > 0:
            editor.click()
            page.wait_for_timeout(500)
            editor.fill(KAAVYA_SOLO_PROMPT)
            print("[✓] Prompt successfully entered into prompt box!")
            page.wait_for_timeout(3000)

        print("\n[Step 4] Starting Generation...")
        gen_btn = page.locator("button[aria-label='Start generation']").first
        if gen_btn.count() > 0 and gen_btn.is_enabled():
            gen_btn.click(force=True)
            print("[✓] Clicked 'Start generation' button!")
        else:
            page.keyboard.press("Control+Enter")
            print("[✓] Triggered generation via Ctrl+Enter!")

        page.wait_for_timeout(4000)

        # Check for approval dialog
        approve_btn = page.locator("button:has-text('Approve'), button:has-text('Always approve')").first
        if approve_btn.count() > 0 and approve_btn.is_visible():
            print("[*] Approving generation dialog...")
            approve_btn.click(force=True)
            page.wait_for_timeout(2000)

        print("\n[Step 5] Generation in progress right before your eyes! Keeping browser open for 60 seconds...")
        time.sleep(60)

        print("\n[✓] Session complete.")
        browser.close()

if __name__ == "__main__":
    run_visible_kaavya_session()
