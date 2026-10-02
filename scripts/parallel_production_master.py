import os
import sys
import time
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
OUTPUT_DIR = BASE_DIR / "data" / "output"
RAW_CLIPS.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

# Episode 18 Scenes
EPISODE_ID = "ep_18_magic_freeze_remote"
SCENES = [
    {
        "part": 1,
        "slot": 4,
        "email": "infolillylooks@gmail.com",
        "label": "Hook: Freeze Game",
        "prompt": "Create a 9:16 vertical animated video with Veo: Pixar 3D animated comedy. Modern Indian living room. Exactly ONE Kaartik (5, yellow polo) holds up a toy game controller pointing at Pinki (25, powder-blue kurti) and shouts: 'Freeze Mummy!' Kaavya (3, pink frock) watches with sparkling giggly eyes."
    },
    {
        "part": 2,
        "slot": 5,
        "email": "elegantdriveways4u@gmail.com",
        "label": "Prank: Statue Mummy",
        "prompt": "Create a 9:16 vertical animated video with Veo: Pixar 3D animation. Modern Indian living room. Pinki (25, powder-blue kurti) comically freezes mid-step holding a basket of soft folded towels, wobbling with funny cartoon wide eyes! Kaartik (5, yellow polo) tiptoes around her examining his living statue triumphantly with cheeky giggles."
    },
    {
        "part": 3,
        "slot": 6,
        "email": "abhiv446@gmail.com",
        "label": "Resolution: Tickle Attack Climax",
        "prompt": "Create a 9:16 vertical animated video with Veo: Pixar 3D comedy. Modern Indian living room. Kaavya (3, pink frock) runs over and tickles Pinki's waist! Pinki bursts into laughter unfreezing, dropping soft pillows over both kids into a giant joyful family cuddle on the rug. Cheerful Indian family comedy climax."
    }
]

def setup_page_canvas(page, slot_idx, email):
    url = f"https://flow.google.com/u/{slot_idx}/"
    print(f"[*] [Slot {slot_idx} - {email}] Navigating to {url}...", flush=True)
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(3000)

    # Click "+ New project"
    new_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i]").first
    if new_btn.count() > 0 and new_btn.is_visible():
        new_btn.click()
        page.wait_for_timeout(4000)

    print(f"[+] [Slot {slot_idx}] Canvas ready: {page.url}", flush=True)

    # Configure Tune settings to Never confirm & 9:16
    tune_btn = page.locator("button:has-text('tune'), [aria-label*='settings' i], [aria-label*='tune' i]").last
    if tune_btn.count() > 0 and tune_btn.is_visible():
        tune_btn.click()
        page.wait_for_timeout(1000)
        never_radio = page.locator("span:has-text('Never'), [role='radio']:has-text('Never'), div:has-text('Never')").last
        if never_radio.count() > 0:
            never_radio.click(force=True)
            page.wait_for_timeout(300)
        v_916 = page.locator("button:has-text('9:16'), [role='button']:has-text('9:16'), div:has-text('9:16')").last
        if v_916.count() > 0:
            v_916.click(force=True)
            page.wait_for_timeout(300)
        save_btn = page.locator("button:has-text('Save'), [role='button']:has-text('Save')").first
        if save_btn.count() > 0 and save_btn.is_visible():
            save_btn.click()
            page.wait_for_timeout(1000)

def submit_prompt_to_page(page, slot_idx, prompt_text, part_num):
    print(f"[*] [Slot {slot_idx}] Submitting Prompt for Scene {part_num}...", flush=True)
    editor = page.locator("[contenteditable='true'], div.ProseMirror, textarea").first
    if editor.count() > 0:
        editor.click()
        page.wait_for_timeout(300)
        editor.fill(prompt_text)
        page.wait_for_timeout(500)
        send_btn = page.locator("button:has-text('arrow_forward'), button[aria-label*='Submit' i], button.send-button").first
        if send_btn.count() > 0 and send_btn.is_visible():
            send_btn.click()
        else:
            page.keyboard.press("Enter")
        print(f"[🚀 SENT] [Slot {slot_idx}] Scene {part_num} prompt dispatched!", flush=True)

def run_parallel_generation():
    print("=" * 70, flush=True)
    print("  THE NAUGHTY DUO — TRIPLE-SLOT PARALLEL PRODUCTION ENGINE", flush=True)
    print("  Concurrent Prompts Across Slots 4, 5, 6 for 3X Speed", flush=True)
    print("=" * 70, flush=True)

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            accept_downloads=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        active_sessions = []
        # Step 1: Open and setup all 3 canvases in parallel
        for s in SCENES:
            page = ctx.new_page()
            setup_page_canvas(page, s["slot"], s["email"])
            active_sessions.append((page, s))

        # Step 2: Submit all 3 prompts simultaneously!
        print("\n" + "=" * 60, flush=True)
        print("  DISPATCHING ALL 3 SCENE PROMPTS SIMULTANEOUSLY", flush=True)
        print("=" * 60, flush=True)
        for page, s in active_sessions:
            submit_prompt_to_page(page, s["slot"], s["prompt"], s["part"])

        # Step 3: Monitor all 3 renders concurrently
        print("\n[*] Monitoring all 3 accounts in parallel (rendering ~75s)...", flush=True)
        start_time = time.time()
        for i in range(1, 25):
            time.sleep(5)
            elapsed = int(time.time() - start_time)
            status_line = []
            for page, s in active_sessions:
                stop_btn = page.locator("button:has-text('Stop'), button[aria-label='Stop']")
                is_rendering = stop_btn.count() > 0 and stop_btn.first.is_visible()
                vids = page.locator("video, [aria-label*='Open video in editor' i]").count()
                status_line.append(f"Slot {s['slot']} (Scene {s['part']}): {'Render' if is_rendering else 'Ready'} ({vids} vids)")
            print(f"[{elapsed}s] " + " | ".join(status_line), flush=True)

        ctx.close()
        print("\n[✓] Parallel generation cycle executed successfully!", flush=True)

if __name__ == "__main__":
    run_parallel_generation()
