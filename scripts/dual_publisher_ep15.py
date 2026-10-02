import os
import sys
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
VIDEO_FILE = BASE_DIR / "data" / "output" / "ep_15_fake_moustache_cop_master.mp4"
LOG_FILE = BASE_DIR / "data" / "uploaded_videos_log.json"

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

YT_TITLE = "Inspector Kaartik Ne Pakda Mummy Ko! 👮‍♂️🍪 #shorts #comedy #cartoon"
YT_DESC = (
    "Inspector Kaartik aur Constable Kaavya ne kiya Mummy ke kitchen par raid! 🍪😂 "
    "Par aage jo hua dekh kar hassi nahi rukegi! Who ate the cookies? Watch till the end for the hilarious moustache twist!\n\n"
    "#thenaughtyduo #cartoon #funny #comedy #animation #viral #3danimation #kids #trending"
)

TIKTOK_CAPTION = (
    "Inspector Kaartik ne Mummy ko kiya arrest! 👮‍♂️🍪 Wait for the moustache twist at the end! 🤣❤️ "
    "Who is the boss of your house? #TheNaughtyDuo #shorts #cartoon #mummy #funny #comedy #animation #relatable #viral"
)

def upload_youtube():
    print("\n" + "=" * 65)
    print("  UPLOADING EPISODE 15 TO YOUTUBE SHORTS")
    print(f"  Title: {YT_TITLE}")
    print("=" * 65)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        page.goto("https://studio.youtube.com", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)

        # Skip dialog if present
        skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
        if skip.count() > 0 and skip.is_visible():
            skip.click()
            page.wait_for_timeout(2000)

        # Click Create
        create_btn = page.locator("ytcp-button#create-icon, button:has-text('Create'), ytcp-button:has-text('Create')").first
        if create_btn.count() > 0:
            create_btn.click()
            page.wait_for_timeout(1500)
            upload_option = page.get_by_text("Upload videos", exact=False).first
            if upload_option.count() > 0 and upload_option.is_visible():
                upload_option.click()
            page.wait_for_timeout(2000)

        # File input
        file_input = page.locator("input[type='file']").first
        if file_input.count() == 0:
            for f in page.frames:
                inp = f.locator("input[type='file']")
                if inp.count() > 0:
                    file_input = inp.first
                    break

        if file_input.count() == 0:
            print("[!] File input element not found.")
            browser.close()
            return None

        print(f"[+] Attaching video file: {VIDEO_FILE}...")
        file_input.set_input_files(str(VIDEO_FILE))
        page.wait_for_timeout(8000)

        # Detect video link
        video_link = None
        for _ in range(15):
            links = page.locator("a.ytcp-video-info, a[href*='youtu.be'], a[href*='youtube.com/shorts']")
            if links.count() > 0:
                for idx in range(links.count()):
                    href = links.nth(idx).get_attribute("href")
                    if href and ("youtu.be" in href or "shorts" in href):
                        video_link = href
                        break
            if video_link:
                break
            page.wait_for_timeout(1000)

        print(f"[+] Video Link detected: {video_link}")

        # Set Title
        title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        if title_box.count() > 0:
            title_box.click()
            page.wait_for_timeout(300)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            title_box.fill(YT_TITLE[:100])
            page.wait_for_timeout(500)
            print("[+] Title set!")

        # Set Description
        desc_box = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
        if desc_box.count() > 0:
            desc_box.click()
            page.wait_for_timeout(300)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            desc_box.fill(YT_DESC)
            page.wait_for_timeout(500)
            print("[+] Description set!")

        # Audience: Not made for kids
        not_kids = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
        if not_kids.count() > 0:
            not_kids.click()
            page.wait_for_timeout(500)
            print("[+] Audience set: Not made for kids.")

        # Wizard steps
        for step in range(3):
            next_btn = page.locator("ytcp-button#next-button, button:has-text('Next')").first
            if next_btn.count() > 0 and next_btn.is_visible() and next_btn.is_enabled():
                next_btn.click()
                print(f"[+] Clicked Next (Step {step+1})")
                page.wait_for_timeout(2500)

        # Visibility: PUBLIC
        pub_radio = page.locator("ytcp-uploads-dialog tp-yt-paper-radio-button[name='PUBLIC'], tp-yt-paper-radio-button[name='PUBLIC']").first
        if pub_radio.count() > 0:
            pub_radio.click(force=True)
            print("[+] Visibility set: PUBLIC.")
            page.wait_for_timeout(1500)

        # Publish
        publish_btn = page.locator("ytcp-uploads-dialog ytcp-button#done-button, ytcp-uploads-dialog button:has-text('Publish'), ytcp-uploads-dialog #publish-button").first
        if publish_btn.count() == 0:
            publish_btn = page.locator("button:has-text('Publish')").first
        if publish_btn.count() > 0:
            publish_btn.click(force=True)
            print("[+] Clicked Publish!")
            page.wait_for_timeout(3000)

        # Handle checks modal if any
        pub_anyway = page.locator("button:has-text('Publish anyway'), ytcp-button:has-text('Publish anyway')").first
        if pub_anyway.count() > 0 and pub_anyway.is_visible():
            pub_anyway.click(force=True)
            page.wait_for_timeout(4000)

        page.screenshot(path=str(BASE_DIR / "data" / "yt_ep15_posted.png"))
        browser.close()
        return video_link

def upload_tiktok():
    print("\n" + "=" * 65)
    print("  UPLOADING EPISODE 15 TO TIKTOK STUDIO")
    print(f"  Caption: {TIKTOK_CAPTION}")
    print("=" * 65)

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

        page.goto("https://www.tiktok.com/tiktokstudio/upload?from=upload", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(6000)

        if "login" in page.url.lower():
            print("[!] TikTok Studio session expired, login required.")
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

        file_input.set_input_files(str(VIDEO_FILE))
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
            page.keyboard.type(TIKTOK_CAPTION, delay=8)
            print("[+] SEO Caption typed into TikTok editor.")
            page.wait_for_timeout(2000)

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)

        post_btn = page.get_by_role("button", name="Post", exact=True)
        if post_btn.count() == 0:
            post_btn = page.locator("button:text-is('Post')")

        if post_btn.count() > 0:
            target_post_btn = post_btn.last
            for _ in range(15):
                if not target_post_btn.is_disabled():
                    break
                page.wait_for_timeout(2000)

            target_post_btn.click(force=True)
            print("[+] Clicked Post button on TikTok Studio!")
            page.wait_for_timeout(6000)

            # Confirm dialogs
            modal_post = page.locator("button:has-text('Post anyway'), button:has-text('Confirm')")
            if modal_post.count() > 0 and modal_post.first.is_visible():
                modal_post.first.click(force=True)
                page.wait_for_timeout(3000)

            page.screenshot(path=str(BASE_DIR / "data" / "tiktok_ep15_posted.png"))
            browser.close()
            return True

        browser.close()
        return False

def update_log(yt_link, tiktok_ok):
    data = {"uploaded": []}
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass

    size_mb = round(VIDEO_FILE.stat().st_size / (1024 * 1024), 2) if VIDEO_FILE.exists() else 0
    record = {
        "key": "ep_15_fake_moustache_cop",
        "filename": VIDEO_FILE.name,
        "size_mb": size_mb,
        "youtube": yt_link or "PENDING",
        "youtube_title": YT_TITLE,
        "youtube_status": "LIVE" if yt_link else "FAILED",
        "tiktok_status": "LIVE" if tiktok_ok else "FAILED",
        "tiktok_caption": TIKTOK_CAPTION,
        "visual_style": "100% 3D CGI Pixar Character Animation (Frame-Chained Continuity)",
        "continuity_method": "Last-Frame Image-to-Video Anchor (FFmpeg -> Flow Canvas)",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    data["uploaded"].append(record)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"[✓ Log Updated]: {record['key']} -> YouTube: {record['youtube_status']}, TikTok: {record['tiktok_status']}")

def main():
    if not VIDEO_FILE.exists():
        print(f"[!] Video file {VIDEO_FILE} not found yet!")
        return

    yt_link = upload_youtube()
    tiktok_ok = upload_tiktok()
    update_log(yt_link, tiktok_ok)

if __name__ == "__main__":
    main()
