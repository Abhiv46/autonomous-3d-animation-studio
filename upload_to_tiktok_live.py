import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
VIDEO_FILE = BASE_DIR / "data" / "processed_episodes" / "TheNaughtyDuo_EP21_MummyKiHighHeels_Master.mp4"

TIKTOK_CAPTION = (
    "Kaavya ne pehni Mummy ki high heels! 😂👠 Sassy fashion model Kaavya ko bhaiyya ne pakad liya! "
    "Wait for her super cute reaction at the end! 🥰❤️ #TheNaughtyDuo #shorts #viral #funny #comedy #3danimation #hindicartoon #foryou #fyp #trending"
)

def run():
    print(f"[1] Connecting to browser over CDP for TikTok...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = context.new_page()
        
        print("[2] Navigating to TikTok Studio Upload...", flush=True)
        page.goto("https://www.tiktok.com/tiktokstudio/upload?from=upload", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(6000)
        print(f"Current URL: {page.url}", flush=True)

        if "login" in page.url.lower():
            print("[!] TikTok Studio session expired, login required.", flush=True)
            page.close()
            return False

        # File input via file chooser
        print("[3] Attaching video file to TikTok Studio...", flush=True)
        select_file_btn = page.locator("button:has-text('Select video'), button:has-text('Select file'), div:has-text('Select video')").first
        
        file_input = page.locator("input[type='file']").first
        if file_input.count() > 0:
            file_input.set_input_files(str(VIDEO_FILE))
            print(f"[+] File set via input: {VIDEO_FILE.name}", flush=True)
        elif select_file_btn.count() > 0:
            with page.expect_file_chooser(timeout=10000) as fc_info:
                select_file_btn.click()
            fc = fc_info.value
            fc.set_files(str(VIDEO_FILE))
            print(f"[+] File set via file chooser: {VIDEO_FILE.name}", flush=True)

        print("[*] Waiting for video upload to process...", flush=True)
        page.wait_for_timeout(10000)

        # Dismiss any onboarding modals
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
        print("[4] Entering Caption in TikTok Studio...", flush=True)
        caption_box = page.locator("[contenteditable='true'], .public-DraftEditor-content, textarea").first
        if caption_box.count() > 0:
            caption_box.click(force=True)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            page.wait_for_timeout(400)
            page.keyboard.type(TIKTOK_CAPTION, delay=8)
            print("[+] SEO Caption typed into TikTok editor.", flush=True)
            page.wait_for_timeout(2000)

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)

        # Click Post
        print("[5] Locating Post button...", flush=True)
        post_btn = page.get_by_role("button", name="Post", exact=True)
        if post_btn.count() == 0:
            post_btn = page.locator("button:text-is('Post')")

        if post_btn.count() > 0:
            target_post_btn = post_btn.last
            print("[*] Waiting for Post button to become enabled...", flush=True)
            for _ in range(15):
                if not target_post_btn.is_disabled():
                    break
                page.wait_for_timeout(2000)

            target_post_btn.click(force=True)
            print("[+] Clicked Post button on TikTok Studio!", flush=True)
            page.wait_for_timeout(6000)

            modal_post = page.locator("button:has-text('Post anyway'), button:has-text('Confirm')")
            if modal_post.count() > 0 and modal_post.first.is_visible():
                modal_post.first.click(force=True)
                page.wait_for_timeout(3000)

            page.screenshot(path=str(BASE_DIR / "data" / "tiktok_ep21_posted.png"))
            print("[SUCCESS] TikTok upload completed! Screenshot saved.", flush=True)
            page.close()
            return True

        page.close()
        return False

if __name__ == "__main__":
    run()
