import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
RAW_CLIPS.mkdir(parents=True, exist_ok=True)

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

PROMPT_SCENE_1 = (
    "Pixar 3D animated comedy. Modern Indian living room. Exactly ONE Kaartik (5, yellow polo) "
    "holds up a toy game controller pointing at Pinki (25, powder-blue kurti) and shouts: "
    "'Freeze Mummy!' Kaavya (3, pink frock) watches with sparkling giggly eyes."
)

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=BRAVE_DATA,
        executable_path=BRAVE_EXE,
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = ctx.new_page()
    print("[*] Navigating to Google Flow Slot 4 (infolillylooks@gmail.com)...", flush=True)
    page.goto("https://flow.google.com/u/4/", wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(4000)

    # Click "+ New project"
    new_proj_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i]").first
    if new_proj_btn.count() > 0 and new_proj_btn.is_visible():
        print("[*] Creating brand new clean project...", flush=True)
        new_proj_btn.click()
        page.wait_for_timeout(6000)
    else:
        print("[!] New project button not found, checking current URL...", flush=True)

    print("[+] Current Canvas URL:", page.url, flush=True)
    page.screenshot(path=str(BASE_DIR / "data" / "clean_canvas_slot4.png"))

    # Locate prompt editor
    editor = page.locator("[contenteditable='true'], div.ProseMirror, textarea").first
    if editor.count() == 0:
        print("[-] Prompt editor not found in canvas!", flush=True)
        ctx.close()
        sys.exit(1)

    print("[*] Entering Scene 1 Prompt into editor...", flush=True)
    editor.click()
    page.wait_for_timeout(500)
    editor.fill(PROMPT_SCENE_1)
    page.wait_for_timeout(1000)

    # Click generate / send button
    send_btn = page.locator("button:has-text('arrow_forward'), button[aria-label*='Submit' i], button[aria-label*='Generate' i]").first
    if send_btn.count() > 0 and send_btn.is_visible():
        print("[*] Clicking Send button...", flush=True)
        send_btn.click()
    else:
        print("[*] Pressing Enter to send prompt...", flush=True)
        page.keyboard.press("Enter")

    page.wait_for_timeout(3000)

    # Auto-approve credits if modal pops up
    for _ in range(10):
        app_btn = page.locator("button:has-text('Always approve'), button:has-text('Approve')")
        if app_btn.count() > 0 and app_btn.first.is_visible():
            print("[+] Approving credits modal...", flush=True)
            app_btn.first.click(force=True)
            page.wait_for_timeout(1500)
            break
        time.sleep(1)

    page.screenshot(path=str(BASE_DIR / "data" / "prompt_submitted_slot4.png"))
    print("[✓] Prompt submitted! Screenshot saved to data/prompt_submitted_slot4.png", flush=True)
    ctx.close()
