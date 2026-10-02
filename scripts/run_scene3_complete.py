import os
import sys
import time
from playwright.sync_api import sync_playwright

PROJECT_URL = "https://flow.google.com/u/0/project/1876f0f7-bc42-4764-86c9-35d76cb3a615"
BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

STYLE_BLOCK = (
    "Semi-realistic 3D animated style, Pixar/Disney-inspired rendering with soft painterly texture, "
    "warm cinematic color grading. Vibrant lighting, rich subsurface skin scattering, fluid cartoon character animation."
)
AVOID_BLOCK = "Avoid: flat 2D look, inconsistent facial features, extra fingers, distorted hands, blurry background, style shifting mid-scene, anatomy errors, redesigned character"

SCENE3_STORY = (
    "Seamless continuous scene climax. Cozy warm domestic bedroom. High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. Full 3D CGI animation. "
    "Beautiful Indian mother Pinki (25, traditional pastel powder-blue kurti, dark hair braid) rushes into bedroom holding a clean laundry basket, but suddenly freezes with wide comical shocked eyes as the flying cockroach buzzes right past her nose! "
    "Pinki comically tosses the laundry basket into the air with an exaggerated cartoon scream, and leaps dramatically onto the bed! "
    "She cuddles chubby toddler Kaartik (5, yellow polo) and cute toddler Kaavya (3.5, pink pajamas, double hair buns) safely under the fluffy duvet blanket. "
    "All three peek out nervously together from under the duvet, holding up slippers and giggling in adorable heartwarming family comedy relief! "
    "Ultra-detailed Pixar 3D CGI animation, comical cartoon physics, warm cozy bedroom lighting, soft background bokeh. "
    "STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays."
)

FULL_PROMPT = f"{STYLE_BLOCK}\n\n{SCENE3_STORY}\n\n{AVOID_BLOCK}"

def run_scene3():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        page.goto(PROJECT_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        # 1. Attach Pinki
        add_btn = page.locator("button[aria-label='Add ingredients to the prompt box']").first
        if add_btn.count() > 0:
            print("[*] Attaching Pinki...")
            add_btn.click(force=True)
            page.wait_for_timeout(1500)
            overlay = page.locator(".cdk-overlay-pane, mat-dialog-container, [role='dialog']").first
            if overlay.count() > 0:
                p_opt = overlay.locator("text='Pinki'").first
                if p_opt.count() > 0:
                    p_opt.click(force=True)
                    page.wait_for_timeout(1000)
                    overlay.locator("button:has-text('Add to prompt')").first.click(force=True)
                    page.wait_for_timeout(1000)

        # 2. Attach Kaavya
        if add_btn.count() > 0:
            print("[*] Attaching Kaavya...")
            add_btn.click(force=True)
            page.wait_for_timeout(1500)
            overlay = page.locator(".cdk-overlay-pane, mat-dialog-container, [role='dialog']").first
            if overlay.count() > 0:
                kv_opt = overlay.locator("text='kaavya'").first
                if kv_opt.count() > 0:
                    kv_opt.click(force=True)
                    page.wait_for_timeout(1000)
                    overlay.locator("button:has-text('Add to prompt')").first.click(force=True)
                    page.wait_for_timeout(1000)

        # 3. Attach Kaartik
        if add_btn.count() > 0:
            print("[*] Attaching Kaartik...")
            add_btn.click(force=True)
            page.wait_for_timeout(1500)
            overlay = page.locator(".cdk-overlay-pane, mat-dialog-container, [role='dialog']").first
            if overlay.count() > 0:
                kt_opt = overlay.locator("text='kaartik'").first
                if kt_opt.count() > 0:
                    kt_opt.click(force=True)
                    page.wait_for_timeout(1000)
                    overlay.locator("button:has-text('Add to prompt')").first.click(force=True)
                    page.wait_for_timeout(1000)

        # 4. Fill prompt
        print("[*] Filling prompt...")
        editor = page.locator(".ProseMirror").first
        editor.click()
        editor.fill(FULL_PROMPT)
        page.wait_for_timeout(1000)
        page.screenshot(path="data/scene3_ready_to_send.png")

        # 5. Click Start generation
        print("[*] Clicking Start generation button...")
        start_gen = page.locator("button[aria-label='Start generation']").first
        start_gen.click(force=True)
        page.wait_for_timeout(5000)
        page.screenshot(path="data/scene3_after_start_gen.png")

        # 6. Check for approval dialog
        approve_btn = page.locator("button:has-text('Approve'), div:has-text('Approve'), span:has-text('Approve')").first
        if approve_btn.count() > 0 and approve_btn.is_visible():
            print("[+] Approval dialog appeared! Clicking Approve...")
            approve_btn.click(force=True)
            page.wait_for_timeout(4000)
            page.screenshot(path="data/scene3_approved_live.png")

        # 7. Monitor until render completes
        print("[*] Waiting for render to finish...")
        for t in range(25):
            page.wait_for_timeout(4000)
            stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
            print(f"  Tick {t+1}: Stop button count = {stop_btn.count()}")
            if t > 2 and stop_btn.count() == 0:
                print("[🏆 RENDER COMPLETED] Stop button disappeared!")
                break

        page.screenshot(path="data/scene3_render_done.png")
        browser.close()

if __name__ == "__main__":
    run_scene3()
