import time
import threading
import win32gui
import win32con
from pathlib import Path
from playwright.sync_api import sync_playwright

VIDEO_FILE = str(Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\TheNaughtyDuo_TikTok_PicnicBasket_Master.mp4").resolve())
TIKTOK_CAPTION = "Picnic Basket Bhaag Gayi! 🧺😱 Kaavya & Kaartik Ka Park Adventure! Wait for Mummy's sweet hug 🥰❤️ #TheNaughtyDuo #shorts #viral #funny #comedy #3danimation #hindicartoon #foryou #fyp #trending #toddlersoftiktok"

def handle_open_dialog():
    print("[Thread] Waiting for Windows Open dialog...")
    for _ in range(40):
        hwnd = win32gui.FindWindow("#32770", "Open")
        if hwnd:
            print(f"[Thread] Found Open dialog! HWND: {hwnd}")
            time.sleep(0.5)
            edit_hwnd = None
            def enum_children(child_hwnd, _):
                nonlocal edit_hwnd
                cls = win32gui.GetClassName(child_hwnd)
                if cls == "Edit":
                    edit_hwnd = child_hwnd
            win32gui.EnumChildWindows(hwnd, enum_children, None)
            
            if edit_hwnd:
                print(f"[Thread] Found Edit HWND: {edit_hwnd}")
                win32gui.SendMessage(edit_hwnd, win32con.WM_SETTEXT, None, VIDEO_FILE)
                time.sleep(0.5)
                win32gui.PostMessage(edit_hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                win32gui.PostMessage(edit_hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
                print("[Thread] Sent file path and pressed Enter successfully!")
                return True
        time.sleep(0.5)
    print("[Thread] Timeout waiting for Open dialog.")
    return False

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
            page = context.new_page()
            page.goto("https://www.tiktok.com/tiktokstudio/upload", wait_until="domcontentloaded")
            time.sleep(4)
        else:
            page.bring_to_front()
            if "tiktokstudio/upload" not in page.url:
                page.goto("https://www.tiktok.com/tiktokstudio/upload", wait_until="domcontentloaded")
                time.sleep(4)
                
        proof_dir = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2")
        
        # Check Discard
        discard = page.locator("button:has-text('Discard')").first
        if discard.count() > 0 and discard.is_visible():
            discard.click(force=True)
            time.sleep(2)
            
        # Start background dialog handler
        t = threading.Thread(target=handle_open_dialog)
        t.start()
        
        # Click Select video button
        print("[2] Clicking 'Select video' button...", flush=True)
        select_btn = page.locator("button:has-text('Select video'), button:has-text('Select files')").first
        select_btn.click()
        
        t.join(timeout=25)
        print("[3] Windows Dialog handled! Waiting 10s for upload to initiate...", flush=True)
        time.sleep(10)
        
        page.screenshot(path=str(proof_dir / "tiktok_native_upload_started.png"))
        
        # Handle modals if any
        for _ in range(4):
            for btn_text in ['Turn on', 'Cancel', 'Got it', 'Allow', 'Not now']:
                b = page.locator(f"button:has-text('{btn_text}')").first
                if b.count() > 0 and b.is_visible():
                    print(f"Dismissing modal button: {btn_text}")
                    b.click(force=True)
                    time.sleep(1)
                    
        # Wait for Caption box
        print("[4] Looking for Caption editor...", flush=True)
        caption_box = page.locator("[contenteditable='true'], .public-DraftEditor-content, textarea").first
        for i in range(25):
            if caption_box.count() > 0 and caption_box.is_visible():
                print(f"[+] Caption editor visible at check {i+1}!", flush=True)
                break
            time.sleep(2)
            caption_box = page.locator("[contenteditable='true'], .public-DraftEditor-content, textarea").first
            
        if caption_box.count() > 0 and caption_box.is_visible():
            print("[5] Filling Viral SEO Caption...", flush=True)
            caption_box.click(force=True)
            time.sleep(0.5)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            time.sleep(0.5)
            page.keyboard.type(TIKTOK_CAPTION, delay=8)
            print("[+] Caption typed successfully!", flush=True)
            time.sleep(2)
            page.screenshot(path=str(proof_dir / "tiktok_native_caption_set.png"))
            
        # Check Post button
        print("[6] Waiting for Post button...", flush=True)
        post_btn = page.locator("button:has-text('Post')").last
        for i in range(25):
            if post_btn.count() > 0 and post_btn.is_visible() and not post_btn.is_disabled():
                print(f"[+] Post button enabled at check {i+1}!", flush=True)
                break
            time.sleep(2)
            
        if post_btn.count() > 0 and not post_btn.is_disabled():
            print("[7] Clicking Post button...", flush=True)
            post_btn.scroll_into_view_if_needed()
            post_btn.click(force=True)
            print("[+] Clicked Post button! Waiting 8s...", flush=True)
            time.sleep(8)
        else:
            print("[!] Post button not enabled yet.")
            
        proof_path = proof_dir / "tiktok_native_posted_final.png"
        page.screenshot(path=str(proof_path))
        print(f"[SUCCESS] Native TikTok upload complete! Proof saved to {proof_path}", flush=True)

if __name__ == "__main__":
    main()
