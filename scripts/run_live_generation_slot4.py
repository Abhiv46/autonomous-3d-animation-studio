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
        accept_downloads=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = ctx.new_page()
    page.goto("https://flow.google.com/u/4/project/5997b7be-97fa-431b-bd68-4428567b3a51", wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(4000)

    # Locate editor
    editor = page.locator("[contenteditable='true'], div.ProseMirror, textarea").first
    print("[*] Typing prompt into editor...", flush=True)
    editor.click()
    page.wait_for_timeout(500)
    editor.fill(PROMPT_SCENE_1)
    page.wait_for_timeout(1000)

    # Click send
    send_btn = page.locator("button:has-text('arrow_forward'), button[aria-label*='Submit' i], button.send-button").first
    if send_btn.count() > 0 and send_btn.is_visible():
        send_btn.click()
    else:
        page.keyboard.press("Enter")
    print("[+] Prompt submitted. Waiting for approval dialog or render start...", flush=True)

    page.wait_for_timeout(3000)

    # Check for approval modal
    for _ in range(12):
        app_btn = page.locator("button:has-text('Always approve'), button:has-text('Approve')")
        if app_btn.count() > 0 and app_btn.first.is_visible():
            print("[+] Approving generation modal...", flush=True)
            app_btn.first.click(force=True)
            page.wait_for_timeout(2000)
            break
        time.sleep(1)

    page.screenshot(path=str(BASE_DIR / "data" / "live_render_started.png"))
    print("[*] Monitoring render progress (keeping browser open)...", flush=True)

    # Wait loop while rendering (up to 180 seconds)
    render_completed = False
    for sec in range(1, 37):
        time.sleep(5)
        stop_btn = page.locator("button:has-text('Stop'), button[aria-label='Stop']")
        is_rendering = stop_btn.count() > 0 and stop_btn.first.is_visible()
        
        # Check if video card or tile appeared
        video_el = page.locator("video, [aria-label*='Open video in editor' i], flow-grid-tile-container")
        print(f"[{sec*5}s] Rendering: {is_rendering} | Video elements: {video_el.count()}", flush=True)
        
        if sec % 6 == 0:
            page.screenshot(path=str(BASE_DIR / "data" / f"live_render_progress_{sec*5}s.png"))

        if not is_rendering and video_el.count() > 0:
            print("[🎉 SUCCESS] Rendering completed!", flush=True)
            render_completed = True
            break

    page.screenshot(path=str(BASE_DIR / "data" / "live_render_completed.png"))

    if render_completed or page.locator("video, [aria-label*='Open video in editor' i]").count() > 0:
        # Download the new video
        card = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container").last
        if card.count() > 0:
            card.click(force=True)
            page.wait_for_timeout(3000)
            dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
            if dl_btn.count() > 0 and dl_btn.is_visible():
                dl_btn.click(force=True)
                page.wait_for_timeout(1500)
                opt_720 = page.get_by_text("720p").first
                if opt_720.count() > 0:
                    out_clip = RAW_CLIPS / "ep_18_scene_01_real.mp4"
                    print(f"[*] Downloading Scene 1 to {out_clip}...", flush=True)
                    with page.expect_download(timeout=60000) as dl_info:
                        opt_720.click(force=True)
                    dl = dl_info.value
                    dl.save_as(str(out_clip))
                    print(f"[🏆 DOWNLOAD COMPLETE] File saved: {out_clip} (Size: {out_clip.stat().st_size} bytes)", flush=True)

    ctx.close()
