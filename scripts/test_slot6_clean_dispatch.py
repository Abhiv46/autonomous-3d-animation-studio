import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
P1_FILE = RAW_CLIPS / "ep_15_fake_moustache_cop_p1.mp4"

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

SLOT_IDX = 6
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

def run_test():
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

        print(f"[*] Navigating to Slot {SLOT_IDX}...", flush=True)
        page.goto(f"https://flow.google.com/u/{SLOT_IDX}/", wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        # Click new project
        new_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i]").first
        if new_btn.count() > 0 and new_btn.is_visible():
            print("[+] Clicking New Project...", flush=True)
            new_btn.click()
            page.wait_for_timeout(5000)

        print(f"[*] Canvas URL: {page.url}", flush=True)

        # Directly target div.ProseMirror
        editor = page.locator("div.ProseMirror").first
        print(f"[*] ProseMirror count: {editor.count()}", flush=True)

        if editor.count() > 0:
            editor.click(force=True)
            page.wait_for_timeout(300)
            editor.fill(P1_PROMPT)
            print("[+] Prompt filled successfully!", flush=True)
            page.wait_for_timeout(1000)

            # Click start generation
            start_btn = page.locator("button[aria-label*='Start generation' i]").first
            if start_btn.count() > 0:
                print("[+] Clicking Start Generation button...", flush=True)
                start_btn.click(force=True)
            else:
                print("[+] Pressing Enter...", flush=True)
                page.keyboard.press("Enter")

            page.wait_for_timeout(2000)

            # Approvals
            for _ in range(5):
                app = page.locator("button:has-text('Always approve'), button:has-text('Approve')")
                if app.count() > 0 and app.last.is_visible():
                    print(f"[✓ Approved]: {app.last.inner_text()}", flush=True)
                    app.last.click(force=True)
                    page.wait_for_timeout(1000)
                    break
                time.sleep(1)

            # Wait for generation to start
            page.wait_for_timeout(5000)
            scr = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_slot6_rendering.png"
            page.screenshot(path=scr)
            print(f"[✓ SUCCESS] Generation dispatched! Screenshot: {scr}", flush=True)

        browser.close()

if __name__ == "__main__":
    run_test()
