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

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
P1_FILE = RAW_CLIPS / "ep_15_fake_moustache_cop_p1.mp4"

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

SLOT_IDX = 0
SLOT_EMAIL = "TecHWirE9999@gmail.com"

CLEAN_P1_PROMPT = (
    "High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. "
    "Full 3D CGI animation. Bright sunlit modern kitchen of Indian home. "
    "Extreme close-up on chubby 3D toddler boy Kaartik (5 years old, bright yellow polo shirt, rounded blushing cheeks). "
    "He has an oversized black drawn handlebar moustache on his upper lip, blowing a shiny toy whistle with puffed cheeks, scowling comically like a serious tough cop. "
    "Camera zooms back to reveal him marching with slow heavy steps holding a giant red plastic magnifying glass. "
    "Beside him, cute toddler sister Kaavya (3.5 years old, pink frock, double buns) waddles excitedly wearing a tin foil badge and saluting with a wooden cooking spatula. "
    "Vibrant Pixar 3D lighting, rich subsurface skin shaders, soft studio ambient occlusion. "
    "STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays."
)

def run_slot0():
    print("=" * 65, flush=True)
    print(f"[*] Starting Ep 15 Scene 1 on PLUS Slot {SLOT_IDX} ({SLOT_EMAIL})...", flush=True)
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

        print(f"[*] Navigating to Slot {SLOT_IDX} Flow...", flush=True)
        page.goto(f"https://flow.google.com/u/{SLOT_IDX}/", wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        # Click New Project
        new_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i], div:has-text('New project')").first
        if new_btn.count() > 0 and new_btn.is_visible():
            print("[+] Clicking New project...", flush=True)
            new_btn.click()
            page.wait_for_timeout(5000)

        print(f"[*] Project Canvas URL: {page.url}", flush=True)

        # Fill prompt
        editor = page.locator("div.ProseMirror").first
        if editor.count() == 0:
            print("[-] ProseMirror editor not found!", flush=True)
            browser.close()
            return False

        editor.click(force=True)
        page.wait_for_timeout(300)
        editor.fill(CLEAN_P1_PROMPT)
        print("[+] Prompt filled into editor.", flush=True)
        page.wait_for_timeout(1000)

        # Click Start generation
        start_btn = page.locator("button[aria-label*='Start generation' i]").first
        if start_btn.count() > 0:
            print("[+] Clicking Start generation button...", flush=True)
            start_btn.click(force=True)
        else:
            page.keyboard.press("Enter")

        print("[*] Waiting for approval prompt (up to 40s)...", flush=True)
        approved = False
        for tick in range(20):
            opt = page.locator("div.option-row:has-text('Always approve'), span.option-label:has-text('Always approve'), div.option-row:has-text('Approve')").first
            if opt.count() > 0 and opt.is_visible():
                print(f"[+] Found approval option: {opt.inner_text()}, clicking...", flush=True)
                opt.click(force=True)
                approved = True
                page.wait_for_timeout(2000)
                break
            time.sleep(2)

        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_slot0_submitted.png")

        # Now monitor rendering
        print("[*] Monitoring render progress (~70-90s)...", flush=True)
        start_t = time.time()
        time.sleep(60)

        rendered = False
        for _ in range(12):
            cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video")
            if cards.count() > 0:
                print(f"[+] Video card detected after {int(time.time() - start_t)}s!", flush=True)
                rendered = True
                break
            time.sleep(5)

        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\debug_slot0_rendered.png")

        # Download 720p
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
                    with page.expect_download(timeout=60000) as dl_info:
                        target_720.click(force=True)
                    dl = dl_info.value
                    dl.save_as(str(P1_FILE))
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(1000)
                    if P1_FILE.exists() and P1_FILE.stat().st_size > 1000000:
                        print(f"[SUCCESS] Scene 1 Downloaded: {P1_FILE.name} ({P1_FILE.stat().st_size} bytes)", flush=True)
                        browser.close()
                        return True

        browser.close()
        return False

if __name__ == "__main__":
    run_slot0()
