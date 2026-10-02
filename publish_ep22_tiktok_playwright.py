import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

VIDEO_PATH = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\processed_episodes\TheNaughtyDuo_EP22_OriginalAudio_Master.mp4"
TIKTOK_CAPTION = "Magical Glowing Gulab Jamun Chori! 🍯😱 Kaartik ne pakad liya Kaavya ko! #TheNaughtyDuo #shorts #viral #funny #comedy #3danimation #hindicartoon #foryou #fyp #trending #gulabjamun"

def upload_tiktok():
    print("[1] Connecting to Brave over CDP...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        
        page = None
        for pg in context.pages:
            if "tiktok.com" in pg.url:
                page = pg
                break
                
        if not page:
            print("[2] Opening TikTok Studio Upload...", flush=True)
            page = context.new_page()
            page.goto("https://www.tiktok.com/tiktokstudio/upload?from=upload", wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(5000)
        else:
            print(f"[2] Using existing TikTok page: {page.url}", flush=True)
            page.bring_to_front()
            
        print(f"Current TikTok page URL: {page.url}", flush=True)
        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\tiktok_debug_state.png")
        
        # Check if login is required
        if "login" in page.url.lower():
            print("[!] TikTok login required!", flush=True)
            return
            
        # Check Discard button if previously uploaded video is there
        discard_btn = page.locator("button:has-text('Discard')").first
        if discard_btn.count() > 0 and discard_btn.is_visible():
            print("[+] Clicking Discard on previous upload...", flush=True)
            discard_btn.click()
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
        page.wait_for_timeout(10000)
        
        # Dismiss modals
        for _ in range(3):
            turn_on_btn = page.locator("button:has-text('Turn on'), button:has-text('Cancel')")
            if turn_on_btn.count() > 0 and turn_on_btn.first.is_visible():
                turn_on_btn.first.click(force=True)
                page.wait_for_timeout(1000)

            got_it_btn = page.locator("button:has-text('Got it')")
            if got_it_btn.count() > 0 and got_it_btn.first.is_visible():
                got_it_btn.first.click(force=True)
                page.wait_for_timeout(1000)
                
        # Fill Caption
        print("[4] Setting Caption...", flush=True)
        caption_box = page.locator("[contenteditable='true'], .public-DraftEditor-content, textarea").first
        if caption_box.count() > 0:
            caption_box.click(force=True)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            page.wait_for_timeout(400)
            page.keyboard.type(TIKTOK_CAPTION, delay=8)
            print("[+] Caption typed into TikTok editor.", flush=True)
            page.wait_for_timeout(2000)
            
        # Click Post button
        print("[5] Waiting for Post button to become enabled...", flush=True)
        post_btn = page.locator("button:has-text('Post')").last
        for i in range(15):
            if post_btn.count() > 0 and post_btn.is_visible() and not post_btn.is_disabled():
                print(f"[+] Post button enabled at check {i+1}!", flush=True)
                break
            page.wait_for_timeout(2000)
            
        if post_btn.count() > 0:
            print("[6] Clicking Post button...", flush=True)
            post_btn.click(force=True)
            page.wait_for_timeout(6000)
            
        proof_path = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\tiktok_ep22_posted.png"
        page.screenshot(path=proof_path)
        print(f"[SUCCESS] TikTok upload completed! Proof saved to {proof_path}", flush=True)

if __name__ == "__main__":
    upload_tiktok()
