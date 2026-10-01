import os
import sys
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
raw_clips = BASE_DIR / "data" / "raw_clips"
raw_clips.mkdir(parents=True, exist_ok=True)
status_file = BASE_DIR / "data" / "live_production_status.json"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.db.database import DatabaseManager

db = DatabaseManager()

brave_exe = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
brave_data = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

prompt_scene2 = "Pixar 3D animation. Pinki comically freezes mid-step holding a basket of soft folded towels, wobbling with funny cartoon wide eyes! Kaartik tiptoes around her examining his 'living statue' triumphantly with cheeky giggles. (All spoken dialogue in joyful Hindi)."

def update_live(scene_desc, pct, stage, reason):
    data = {
        "active_id": "ep_18_magic_freeze_remote",
        "active_title": "Mummy Ka Magic Remote! Sab Freeze Ho Gaye! #TheNaughtyDuo #shorts",
        "active_account": "/u/3/ (pinku.pub@gmail.com)",
        "active_scene": scene_desc,
        "percentage": pct,
        "parts_text": f"Rendering Scene 2 of 3 on Google Flow...",
        "stage": stage,
        "target_platform": "YouTube Shorts & TikTok",
        "delay_reason": reason
    }
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def dispatch_scene2():
    print("Starting Scene 2 Dispatch...")
    update_live("Scene 2 of 3: Escalation (Freeze Statue)", 66, "Dispatching Scene 2 Prompt to Google Flow...", "🟢 Typing Scene 2 prompt into Google Flow canvas...")
    
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=brave_data,
            executable_path=brave_exe,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        url = "https://flow.google.com/u/3/project/a1c6f19b-b046-41f3-9b33-fbc756646163"
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(6000)
        
        # Target prompt editor inside flow-rich-text-editor
        editor = page.locator("flow-rich-text-editor div.ProseMirror")
        if editor.count() == 0:
            print("Editor not found!")
            ctx.close()
            return
            
        print("Clicking editor and typing prompt...")
        editor.first.click()
        page.wait_for_timeout(400)
        page.keyboard.type(prompt_scene2, delay=5)
        page.wait_for_timeout(1000)
        
        arrow_btn = page.locator("button:has-text('arrow_forward')")
        print("Arrow btn enabled:", arrow_btn.first.is_enabled())
        arrow_btn.first.click(force=True)
        page.wait_for_timeout(5000)
        
        # Save screenshot
        page.screenshot(path=str(BASE_DIR / "data" / "scene2_dispatched.png"))
        print("Screenshot saved to data/scene2_dispatched.png")
        
        update_live("Scene 2 of 3: Escalation (Cloud Generating)", 75, "Generating Video in Google Flow...", "🟢 Active Cloud Generation: Scene 2 prompt accepted, Google Flow 3D AI video actively rendering!")
        
        # Wait for rendering to complete (up to 120s)
        start_time = time.time()
        rendered = False
        while (time.time() - start_time) < 120:
            time.sleep(10)
            stop_btn = page.locator("button:has-text('Stop')")
            if stop_btn.count() == 0 and (time.time() - start_time) > 25:
                print("Rendering complete! Stop button disappeared.")
                rendered = True
                break
            print(f"Waiting for render... ({int(time.time() - start_time)}s)")
            
        if rendered:
            page.wait_for_timeout(4000)
            # Click tile to download
            tile = page.locator("flow-grid-tile-container").first
            tile.click(force=True)
            page.wait_for_timeout(2500)
            
            dl_btn = page.locator("button[aria-label*='Download media' i], button[aria-label*='Download' i]").first
            if dl_btn.count() > 0 and dl_btn.is_visible():
                dl_btn.click(force=True)
                page.wait_for_timeout(1000)
                target_720 = page.locator("[role='menuitem']:has-text('720p'), mat-menu-item:has-text('720p'), text='720p'").first
                if target_720.count() > 0:
                    out_path = str(raw_clips / "ep_18_scene_02.mp4")
                    try:
                        with page.expect_download(timeout=35000) as dl_info:
                            target_720.click(force=True)
                        dl = dl_info.value
                        dl.save_as(out_path)
                        print(f"Scene 2 Downloaded successfully! ({os.path.getsize(out_path)} bytes)")
                        
                        # Update DB and deduct credits
                        db.update_part_status('ep_18_magic_freeze_remote-P02', 'COMPLETED', account_id='acc_3', raw_path=out_path)
                        with db.get_connection() as conn:
                            conn.execute("UPDATE accounts SET available_credits = MAX(0, available_credits - 10) WHERE slot_index = 3")
                            conn.commit()
                            
                        update_live("Scene 2 of 3: Completed (Downloaded)", 80, "Scene 2 Ready | Queueing Scene 3", "🟢 Scene 2 video successfully downloaded & credits deducted!")
                    except Exception as e:
                        print(f"Download error: {e}")

        ctx.close()

if __name__ == "__main__":
    dispatch_scene2()
