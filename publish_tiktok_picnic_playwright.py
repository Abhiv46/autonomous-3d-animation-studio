import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

VIDEO_PATH = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\TheNaughtyDuo_TikTok_PicnicBasket_Master.mp4"
TIKTOK_CAPTION = "Picnic Basket Bhaag Gayi! 🧺😱 Kaavya & Kaartik Ka Park Adventure! Wait for Mummy's sweet hug 🥰❤️ #TheNaughtyDuo #shorts #viral #funny #comedy #3danimation #hindicartoon #foryou #fyp #trending #toddlersoftiktok"

def main():
    print("[1] Connecting to Brave via CDP...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        
        page = None
        for pg in context.pages:
            if "tiktokstudio/upload" in pg.url or "tiktok.com" in pg.url:
                page = pg
                break
                
        if not page:
            print("[2] Opening TikTok Studio Upload...", flush=True)
            page = context.new_page()
            page.goto("https://www.tiktok.com/tiktokstudio/upload", wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(5000)
        else:
            print(f"[2] Found existing TikTok page: {page.url}", flush=True)
            page.bring_to_front()
            if "tiktokstudio/upload" not in page.url:
                page.goto("https://www.tiktok.com/tiktokstudio/upload", wait_until="domcontentloaded")
                page.wait_for_timeout(4000)

        proof_dir = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2")
        page.screenshot(path=str(proof_dir / "tiktok_init_state.png"))
        
        # Check Discard button if previous state was stuck
        discard_btn = page.locator("button:has-text('Discard')").first
        if discard_btn.count() > 0 and discard_btn.is_visible():
            print("[+] Clicking Discard on previous upload...", flush=True)
            discard_btn.click(force=True)
            page.wait_for_timeout(2000)
            
        # Locate file input
        file_input = page.locator("input[type='file']").first
        if file_input.count() == 0:
            for f in page.frames:
                inp = f.locator("input[type='file']")
                if inp.count() > 0:
                    file_input = inp.first
                    break
                    
        if file_input.count() == 0:
            print("[!] File input element not found!", flush=True)
            return
            
        print(f"[3] Uploading master video: {VIDEO_PATH}", flush=True)
        file_input.set_input_files(VIDEO_PATH)
        print("[+] File input set. Waiting for video processing...", flush=True)
        page.wait_for_timeout(8000)
        
        # Dismiss modals if any
        for _ in range(4):
            for btn_text in ['Turn on', 'Cancel', 'Got it', 'Allow', 'Not now']:
                b = page.locator(f"button:has-text('{btn_text}')").first
                if b.count() > 0 and b.is_visible():
                    print(f"Dismissing modal button: {btn_text}")
                    b.click(force=True)
                    page.wait_for_timeout(1000)
                    
        page.screenshot(path=str(proof_dir / "tiktok_upload_progress.png"))
        
        # Wait for Caption box
        print("[4] Waiting for Caption box...", flush=True)
        caption_box = page.locator("[contenteditable='true'], .public-DraftEditor-content, textarea").first
        for i in range(20):
            if caption_box.count() > 0 and caption_box.is_visible():
                print(f"[+] Caption box visible at check {i+1}!", flush=True)
                break
            page.wait_for_timeout(2000)
            caption_box = page.locator("[contenteditable='true'], .public-DraftEditor-content, textarea").first
            
        if caption_box.count() > 0:
            print("[5] Setting Viral SEO Caption...", flush=True)
            caption_box.click(force=True)
            page.wait_for_timeout(500)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            page.wait_for_timeout(400)
            page.keyboard.type(TIKTOK_CAPTION, delay=10)
            print("[+] Caption typed into TikTok editor.", flush=True)
            page.wait_for_timeout(2000)
            page.screenshot(path=str(proof_dir / "tiktok_caption_ready.png"))
        else:
            print("[!] Caption box not found!", flush=True)
            
        # Wait for Post button to become enabled
        print("[6] Waiting for Post button to become enabled...", flush=True)
        post_btn = page.locator("button:has-text('Post')").last
        for i in range(25):
            if post_btn.count() > 0 and post_btn.is_visible() and not post_btn.is_disabled():
                print(f"[+] Post button enabled at check {i+1}!", flush=True)
                break
            page.wait_for_timeout(2000)
            
        if post_btn.count() > 0 and not post_btn.is_disabled():
            print("[7] Clicking Post button...", flush=True)
            post_btn.scroll_into_view_if_needed()
            post_btn.click(force=True)
            print("[+] Post button clicked! Waiting 8s for completion...", flush=True)
            page.wait_for_timeout(8000)
        else:
            print("[!] Post button not enabled or found.")
            
        proof_path = proof_dir / "tiktok_picnic_final_proof.png"
        page.screenshot(path=str(proof_path))
        print(f"[SUCCESS] TikTok upload workflow complete! Screenshot saved to {proof_path}", flush=True)

if __name__ == "__main__":
    main()
