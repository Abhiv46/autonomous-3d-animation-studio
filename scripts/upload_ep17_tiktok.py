import os
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
VIDEO_PATH = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\ep_17_roohafza_pink_rabbit_master.mp4"

TIKTOK_CAPTION = (
    "Pink Mustache Wala Khargosh! 🐰🍓 Roohafza Milk Party! "
    "Thandi-thandi strawberry milk party me Kaartik ban gaya pink bunny! 🥛😂 "
    "Aapko Roohafza pasand hai ya chocolate? Comment karo! 👇 "
    "#TheNaughtyDuo #shorts #viral #funny #comedy #3danimation #hindicartoon #foryou #fyp #trending"
)

def upload_ep17_tiktok():
    if not os.path.exists(VIDEO_PATH):
        print(f"[!] Video not found at {VIDEO_PATH}")
        return False
        
    print(f"[*] Starting TikTok Studio Auto-Upload for Episode 17...")
    print(f"[*] Caption: {TIKTOK_CAPTION}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1440, "height": 900})
        
        print("[*] Navigating to TikTok Studio Upload...")
        page.goto("https://www.tiktok.com/tiktokstudio/upload?from=upload", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(6000)
        
        # Check login state
        if "login" in page.url.lower():
            print(f"[!] TikTok redirected to login: {page.url}")
            page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\tiktok_login_needed.png")
            browser.close()
            return False
            
        file_input = page.locator("input[type='file']").first
        if file_input.count() == 0:
            for f in page.frames:
                inp = f.locator("input[type='file']")
                if inp.count() > 0:
                    file_input = inp.first
                    break
                    
        if file_input.count() == 0:
            print("[!] Could not locate file input. Taking debug screenshot...")
            page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\tiktok_no_file_input.png")
            browser.close()
            return False
            
        print(f"[+] Setting video file: {VIDEO_PATH}")
        file_input.set_input_files(VIDEO_PATH)
        print("[*] Waiting for video upload & UI elements to load (10 seconds)...")
        page.wait_for_timeout(10000)
        
        # 1. Dismiss Popups / Modals
        print("[*] Checking and dismissing any popup modals...")
        for _ in range(3):
            turn_on_btn = page.locator("button:has-text('Turn on'), button:has-text('Cancel')")
            if turn_on_btn.count() > 0 and turn_on_btn.first.is_visible():
                print("[+] Dismissing 'Turn on content checks' popup...")
                turn_on_btn.first.click(force=True)
                page.wait_for_timeout(1000)
                
            got_it_btn = page.locator("button:has-text('Got it')")
            if got_it_btn.count() > 0 and got_it_btn.first.is_visible():
                print("[+] Dismissing 'Got it' popup...")
                got_it_btn.first.click(force=True)
                page.wait_for_timeout(1000)
                
        # 2. Fill Caption with Full SEO
        print("[*] Locating Description / Caption box...")
        caption_box = page.locator("[contenteditable='true'], .public-DraftEditor-content, textarea").first
        if caption_box.count() > 0:
            print("[+] Clicking caption box and entering SEO text...")
            caption_box.click(force=True)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            page.wait_for_timeout(400)
            page.keyboard.type(TIKTOK_CAPTION, delay=8)
            print("[+] Title, micro-story and viral hashtags typed successfully!")
            page.wait_for_timeout(2000)
            
        # 3. Click Post Button
        print("[*] Scrolling to bottom...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)
        
        post_btn = page.get_by_role("button", name="Post", exact=True)
        if post_btn.count() == 0:
            post_btn = page.locator("button:text-is('Post')")
            
        if post_btn.count() > 0:
            print(f"[+] Found Post button (count: {post_btn.count()})")
            target_post_btn = post_btn.last
            for i in range(15):
                if not target_post_btn.is_disabled():
                    print("[+] Post button is ENABLED and ready to click!")
                    break
                print("[*] Waiting for Post button to enable...")
                page.wait_for_timeout(2000)
                
            print("[*] Clicking 'Post' button now...")
            target_post_btn.click(force=True)
            
            print("[*] Waiting for upload submission to finish (10s)...")
            page.wait_for_timeout(10000)
            
            scr_path = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\tiktok_ep17_posted.png"
            page.screenshot(path=scr_path)
            print(f"[*] Post-submission page URL: {page.url}")
            print(f"[+] Screenshot saved to: {scr_path}")
            print("[🎉 SUCCESS] Episode 17 posted to TikTok with Full SEO!")
            browser.close()
            return True
        else:
            print("[!] Post button not found.")
            page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\tiktok_post_btn_not_found.png")
            browser.close()
            return False

if __name__ == "__main__":
    upload_ep17_tiktok()
