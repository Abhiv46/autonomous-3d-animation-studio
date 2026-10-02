import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def upload_to_tiktok_studio(video_path: str, caption_text: str) -> bool:
    if not os.path.exists(video_path):
        print(f"[!] TikTok Upload Error: Video not found at {video_path}")
        return False

    print(f"[*] [TikTok Studio] Starting upload for {os.path.basename(video_path)}...")
    print(f"[*] [TikTok Studio] Caption: {caption_text}")

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

        try:
            page.goto("https://www.tiktok.com/tiktokstudio/upload?from=upload", wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(6000)

            if "login" in page.url.lower():
                print(f"[!] TikTok Studio session expired, login required: {page.url}")
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
                print("[!] File input locator not found on TikTok Studio.")
                browser.close()
                return False

            file_input.set_input_files(video_path)
            print("[+] Video file attached. Waiting 10s for upload processing...")
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
            caption_box = page.locator("[contenteditable='true'], .public-DraftEditor-content, textarea").first
            if caption_box.count() > 0:
                caption_box.click(force=True)
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                page.wait_for_timeout(400)
                page.keyboard.type(caption_text, delay=8)
                print("[+] SEO Caption typed into TikTok editor.")
                page.wait_for_timeout(2000)

            # Ensure post button is clicked
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)

            post_btn = page.get_by_role("button", name="Post", exact=True)
            if post_btn.count() == 0:
                post_btn = page.locator("button:text-is('Post')")

            if post_btn.count() > 0:
                target_post_btn = post_btn.last
                for i in range(15):
                    if not target_post_btn.is_disabled():
                        break
                    page.wait_for_timeout(2000)

                target_post_btn.click(force=True)
                print("[+] Clicked Post on TikTok Studio. Waiting for submission...")
                page.wait_for_timeout(10000)

                print(f"[✓] TikTok Studio submission completed! URL: {page.url}")
                browser.close()
                return True
            else:
                print("[!] Post button not found on TikTok Studio.")
                browser.close()
                return False
        except Exception as e:
            print(f"[!] Error during TikTok upload: {e}")
            browser.close()
            return False

if __name__ == "__main__":
    test_video = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\ep_14_bubble_wrap_blast_master.mp4"
    test_caption = (
        "Mummy Ka Bubble Wrap Trap! 💥🤣 Ghar Me Phate Patakhe! "
        "Jab Kaartik aur Kaavya ne carpet ke neeche bubble wrap bichha diya! 😂👣 "
        "Aapko bubble wrap phodna pasand hai? Comment karo! 👇 "
        "#TheNaughtyDuo #shorts #viral #funny #comedy #3danimation #hindicartoon #foryou #fyp #trending"
    )
    upload_to_tiktok_studio(test_video, test_caption)
