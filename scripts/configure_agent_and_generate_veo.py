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

PROMPT_TEXT = (
    "Create a 9:16 animated video with Veo: Pixar 3D animated comedy. Modern Indian living room. "
    "Exactly ONE Kaartik (5, yellow polo) holds up a toy game controller pointing at Pinki (25, powder-blue kurti) "
    "and shouts: 'Freeze Mummy!' Pinki comically freezes mid-step wobbling with funny cartoon wide eyes! "
    "Kaavya (3, pink frock) watches giggling cheerfully. Vibrant Pixar 3D animation."
)

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=BRAVE_DATA,
        executable_path=BRAVE_EXE,
        headless=True,
        accept_downloads=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = ctx.new_page()
    print("[*] Opening Google Flow Slot 4...", flush=True)
    page.goto("https://flow.google.com/u/4/project/5997b7be-97fa-431b-bd68-4428567b3a51", wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(4000)

    # Open Tune / Settings
    tune_btn = page.locator("button:has-text('tune'), [aria-label*='settings' i], [aria-label*='tune' i]").last
    if tune_btn.count() > 0:
        print("[*] Opening Agent settings...", flush=True)
        tune_btn.click()
        page.wait_for_timeout(1500)

        # Select 'Never' confirm
        never_radio = page.locator("span:has-text('Never'), [role='radio']:has-text('Never'), div:has-text('Never')").last
        if never_radio.count() > 0:
            print("[+] Selecting 'Never confirm' for full autonomous execution...", flush=True)
            never_radio.click(force=True)
            page.wait_for_timeout(500)

        # Under Video generation default, select 9:16
        # Find 9:16 in video section
        v_916 = page.locator("button:has-text('9:16'), [role='button']:has-text('9:16'), div:has-text('9:16')").last
        if v_916.count() > 0:
            print("[+] Selecting 9:16 vertical aspect ratio for Veo...", flush=True)
            v_916.click(force=True)
            page.wait_for_timeout(500)

        # Click Save
        save_btn = page.locator("button:has-text('Save'), [role='button']:has-text('Save')").first
        if save_btn.count() > 0 and save_btn.is_visible():
            print("[✓] Clicking Save settings...", flush=True)
            save_btn.click()
            page.wait_for_timeout(1500)

    # Now type prompt and send
    editor = page.locator("[contenteditable='true'], div.ProseMirror, textarea").first
    print("[*] Entering Veo video prompt...", flush=True)
    editor.click()
    page.wait_for_timeout(500)
    editor.fill(PROMPT_TEXT)
    page.wait_for_timeout(1000)

    send_btn = page.locator("button:has-text('arrow_forward'), button[aria-label*='Submit' i], button.send-button").first
    if send_btn.count() > 0 and send_btn.is_visible():
        send_btn.click()
    else:
        page.keyboard.press("Enter")

    print("[🎉] Veo Video Prompt sent! Monitoring video rendering...", flush=True)
    page.wait_for_timeout(5000)
    page.screenshot(path=str(BASE_DIR / "data" / "veo_render_launched.png"))

    # Monitor rendering loop (up to 120s)
    for sec in range(1, 25):
        time.sleep(5)
        stop_btn = page.locator("button:has-text('Stop'), button[aria-label='Stop']")
        is_rendering = stop_btn.count() > 0 and stop_btn.first.is_visible()
        videos = page.locator("video, [aria-label*='Open video in editor' i]")
        print(f"[{sec*5}s] Rendering: {is_rendering} | Videos on page: {videos.count()}", flush=True)

        if not is_rendering and videos.count() > 0:
            print("[🏆] Veo video render completed!", flush=True)
            page.screenshot(path=str(BASE_DIR / "data" / "veo_render_done.png"))
            break

    page.screenshot(path=str(BASE_DIR / "data" / "veo_render_final_state.png"))
    ctx.close()
