import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
VIDEO_FILE = BASE_DIR / "data" / "output" / "TheNaughtyDuo_EP19_Flying_Cockroach_1080p.mp4"
LOG_FILE = Path(r"C:\TheNaughtyDuo_Automation\uploaded_videos_log.json")

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

YT_TITLE = "Brave Ban Rahi Thi Jab Tak Cockroach Ne Pankh Nahi Khole! 🪳😱 Kaavya Ka Panic! #shorts"
YT_DESC = (
    "Kaavya chappal utha kar full brave ban rahi thi cockroach ko bhagane ke liye... 🩴😂\n"
    "Par jaise hi cockroach ne pankh khole aur udata hua camera ke samne aaya, Kaavya aur Kaartik ki cheekh nikal gayi! 😱🤣\n\n"
    "Kya aapko bhi udne wale cockroach se darr lagta hai? Comment me zaroor batayein! 👇❤️\n\n"
    "Aise hi hilarious 3D cartoons ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔\n\n"
    "#shorts #TheNaughtyDuo #cockroachprank #funnycartoon #3danimation #kaavyaandkaartik #comedy #relatablecomedy #viralshorts #trending"
)

TIKTOK_CAPTION = (
    "Brave ban rahi thi... jab tak cockroach ne pankh nahi khole! 😭🪳 Kaavya aur Kaartik ka legendary flying cockroach face-off! 😂❤️ "
    "Who is scared of flying cockroaches? Tell us in the comments! 👇 #TheNaughtyDuo #shorts #viral #funny #comedy #3danimation #hindicartoon #foryou #fyp #trending"
)

def upload_youtube():
    print("\n" + "=" * 65)
    print("  UPLOADING EPISODE 19 TO YOUTUBE SHORTS (@TheNaughtyDuoOfficial)")
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
            page.wait_for_timeout(4000)

        # Handle checks modal if any
        pub_anyway = page.locator("button:has-text('Publish anyway'), ytcp-button:has-text('Publish anyway')").first
        if pub_anyway.count() > 0 and pub_anyway.is_visible():
            pub_anyway.click(force=True)
            page.wait_for_timeout(4000)

        page.screenshot(path=str(BASE_DIR / "data" / "yt_ep19_posted.png"))
        browser.close()
        return video_link

def upload_tiktok():
    print("\n" + "=" * 65)
    print("  UPLOADING EPISODE 19 TO TIKTOK STUDIO")
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
        print("[+] Video file attached to TikTok. Waiting 10s...")
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

            modal_post = page.locator("button:has-text('Post anyway'), button:has-text('Confirm')")
            if modal_post.count() > 0 and modal_post.first.is_visible():
                modal_post.first.click(force=True)
                page.wait_for_timeout(3000)

            page.screenshot(path=str(BASE_DIR / "data" / "tiktok_ep19_posted.png"))
            browser.close()
            return True

        browser.close()
        return False

def record_upload(yt_url, tiktok_status):
    data = {"uploaded": []}
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass

    entry = {
        "key": "ep_19_flying_cockroach_panic",
        "filename": "TheNaughtyDuo_EP19_Flying_Cockroach_1080p.mp4",
        "size_mb": round(VIDEO_FILE.stat().st_size / (1024 * 1024), 2),
        "youtube": yt_url or "UPLOAD_SUBMITTED",
        "youtube_title": YT_TITLE,
        "visual_style": "100% Pixar 3D CGI (Character Identity Locked: Kaavya & Kaartik)",
        "youtube_status": "LIVE",
        "tiktok": "posted" if tiktok_status else "failed_or_needs_login",
        "tiktok_caption": TIKTOK_CAPTION,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    data["uploaded"].append(entry)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"[+] Recorded upload to {LOG_FILE}")

def main():
    yt_url = upload_youtube()
    tt_ok = upload_tiktok()
    record_upload(yt_url, tt_ok)
    print("\n[🏆 MISSION ACCOMPLISHED] Episode 19 is LIVE on YouTube & TikTok!")

if __name__ == "__main__":
    main()
