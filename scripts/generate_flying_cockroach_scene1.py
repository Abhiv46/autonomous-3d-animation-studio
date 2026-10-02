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

# Strict locked components
STYLE_BLOCK = (
    "Semi-realistic 3D animated style, Pixar/Disney-inspired rendering with soft painterly texture, "
    "warm cinematic color grading. Vibrant lighting, rich subsurface skin scattering, fluid cartoon character animation."
)
AVOID_BLOCK = "Avoid: flat 2D look, inconsistent facial features, extra fingers, distorted hands, blurry background, style shifting mid-scene, anatomy errors, redesigned character"

SCENE1_STORY = (
    "Cozy warm domestic bedroom, soft golden lamp glow, warm wooden textures. "
    "High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. Full 3D CGI animation. "
    "Cute 3D chubby toddler girl Kaavya (3.5 years old, double hair buns with pink scrunchies, chubby rosy blushing cheeks, large expressive watery Disney eyes) "
    "stands nervously on top of a small wooden stool in pink pajamas, holding a pink slide slipper above her head with comical terrified focus. "
    "A tiny shiny cockroach scuttles slowly across the floor tiles below. Kaavya has a cute nervous sweat drop on her brow with trembling pouty lips. "
    "At the doorway, chubby toddler brother Kaartik (5 years old, bright yellow polo shirt, messy fringe) peeks around the doorframe with wide excited eyes, whispering to cheer her on. "
    "Ultra-detailed textures: soft cotton pajamas, rustic wood grain stool, glossy insect shell, cinematic lighting with soft background bokeh. "
    "STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays."
)

FULL_PROMPT = f"{STYLE_BLOCK}\n\n{SCENE1_STORY}\n\n{AVOID_BLOCK}"

def generate_scene1():
    print("=" * 65)
    print("  LAUNCHING SCENE 1 GENERATION IN 'THE NAUGHTY DUO' (SLOT 0)")
    print("  CHARACTER REFERENCES: kaavya + kaartik")
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

        page.screenshot(path="data/tnd_before_prompt.png")

        # Step 1: Open Add Ingredients menu (+)
        add_btn = page.locator("button[aria-label*='Add' i], [aria-label*='ingredient' i], button:has-text('add')").last
        if add_btn.count() == 0:
            # Fallback to coordinate or icon
            add_btn = page.locator("mat-icon:has-text('add')").last
        
        print("[*] Clicking Add (+) button to attach character references...")
        add_btn.click(force=True)
        page.wait_for_timeout(2000)

        # Attach Kaavya reference
        print("[*] Selecting 'kaavya' character asset...")
        kaavya_item = page.locator("text='kaavya'").first
        if kaavya_item.count() > 0:
            kaavya_item.click(force=True)
            page.wait_for_timeout(1500)
            add_to_prompt = page.locator("button:has-text('Add to prompt')").first
            if add_to_prompt.count() > 0:
                add_to_prompt.click(force=True)
                print("[+] Successfully attached 'kaavya' character reference!")
                page.wait_for_timeout(1500)

        # Step 2: Open Add (+) menu again for Kaartik
        print("[*] Clicking Add (+) button for 'kaartik'...")
        add_btn.click(force=True)
        page.wait_for_timeout(2000)

        kaartik_item = page.locator("text='kaartik'").first
        if kaartik_item.count() > 0:
            kaartik_item.click(force=True)
            page.wait_for_timeout(1500)
            add_to_prompt = page.locator("button:has-text('Add to prompt')").first
            if add_to_prompt.count() > 0:
                add_to_prompt.click(force=True)
                print("[+] Successfully attached 'kaartik' character reference!")
                page.wait_for_timeout(1500)

        page.screenshot(path="data/tnd_after_adding_refs.png")

        # Step 3: Enter the locked prompt into ProseMirror editor
        print("[*] Entering locked prompt into editor...")
        editor = page.locator(".ProseMirror").first
        editor.click()
        page.wait_for_timeout(500)
        # Type or fill prompt
        editor.fill(FULL_PROMPT)
        page.wait_for_timeout(1000)

        page.screenshot(path="data/tnd_prompt_filled.png")

        # Step 4: Submit prompt (arrow button or Enter)
        print("[*] Submitting prompt...")
        submit_btn = page.locator("button[aria-label*='Submit' i], button[aria-label*='Send' i], button[aria-label*='Generate' i], button:has-text('arrow_forward'), button:has-text('arrow_upward')").last
        if submit_btn.count() > 0 and submit_btn.is_enabled():
            submit_btn.click(force=True)
        else:
            page.keyboard.press("Control+Enter")
        page.wait_for_timeout(4000)

        page.screenshot(path="data/tnd_after_submit.png")

        # Step 5: Check if approval dialog appears
        print("[*] Checking for credit approval dialog...")
        approve_btn = page.locator("button:has-text('Approve'), div:has-text('Approve'), span:has-text('Approve')").first
        if approve_btn.count() > 0 and approve_btn.is_visible():
            print("[+] Approval dialog detected! Clicking Approve...")
            approve_btn.click(force=True)
            page.wait_for_timeout(3000)
            page.screenshot(path="data/tnd_approved.png")

        # Check render status
        print("[*] Monitoring generation start...")
        for check in range(6):
            page.wait_for_timeout(5000)
            stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
            print(f"  Check {check+1}: Active render stop button count = {stop_btn.count()}")
            if stop_btn.count() > 0:
                print("[🚀 CONFIRMED] Generation has actively begun on Google Flow!")
                break

        page.screenshot(path="data/tnd_generation_progress.png")
        browser.close()
        print("[+] Scene 1 submission complete.")

if __name__ == "__main__":
    generate_scene1()
