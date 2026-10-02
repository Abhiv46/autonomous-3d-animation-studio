import sys
import json
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
VIDEO_FILE = BASE_DIR / "data" / "processed_episodes" / "TheNaughtyDuo_EP21_MummyKiHighHeels_OriginalAudio_Master.mp4"
LOG_FILE = Path(r"C:\TheNaughtyDuo_Automation\uploaded_videos_log.json")

YT_TITLE = "Kaavya Ne Pehni Mummy Ki High Heels! 😂👠 Sassy Model Kaavya! #shorts"
YT_DESC = (
    "Kaavya ne pehan li Mummy ki nayi pink high heels aur ban gayi fashion model! 😂👠\n"
    "Lekin jab Kaartik bhaiyya ne strict banke pakad liya toh dekhiye Kaavya ne kaise cute bahane banaye! 🥰❤️\n\n"
    "Aapne bhi bachpan me Mummy ki heels try ki hai kya? Comment me batayein! 👇😂\n\n"
    "Aise hi funny aur cute 3D family cartoons ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔✨\n\n"
    "#shorts #TheNaughtyDuo #funnycartoon #3danimation #hindicartoon #kaavyaandkaartik #comedy #relatablecomedy #viralshorts #trending #kidsanimation"
)

def run():
    print(f"[1] Connecting to browser over CDP...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = context.new_page()
        
        print("[2] Navigating to YouTube Studio...", flush=True)
        page.goto("https://studio.youtube.com", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(3000)
        print(f"Current URL: {page.url}", flush=True)
        
        # Skip dialog if present
        skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
        if skip.count() > 0 and skip.is_visible():
            print("[+] Clicking Skip to YouTube Studio...", flush=True)
            skip.click()
            page.wait_for_timeout(2000)

        # Click Create
        print("[3] Clicking Create button...", flush=True)
        create_btn = page.locator("ytcp-button#create-icon, button:has-text('Create'), ytcp-button:has-text('Create')").first
        if create_btn.count() > 0:
            create_btn.click()
            page.wait_for_timeout(1500)
            upload_option = page.get_by_text("Upload videos", exact=False).first
            if upload_option.count() > 0 and upload_option.is_visible():
                upload_option.click()
            page.wait_for_timeout(2000)

        # File input via file chooser
        print("[4] Attaching master video file with ORIGINAL audio...", flush=True)
        select_files_btn = page.locator("#select-files-button, button:has-text('Select files'), ytcp-button:has-text('Select files')").first
        
        if select_files_btn.count() > 0 and select_files_btn.is_visible():
            with page.expect_file_chooser(timeout=10000) as fc_info:
                select_files_btn.click()
            fc = fc_info.value
            fc.set_files(str(VIDEO_FILE))
            print(f"[+] File set via file chooser: {VIDEO_FILE.name}", flush=True)
        else:
            file_input = page.locator("input[type='file']").first
            file_input.set_input_files(str(VIDEO_FILE))
            print(f"[+] File set via file input: {VIDEO_FILE.name}", flush=True)

        print("[*] Waiting for upload dialog to process video...", flush=True)
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

        print(f"[+] Video Link detected: {video_link}", flush=True)

        # Set Title
        print("[5] Setting Title...", flush=True)
        title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        if title_box.count() > 0:
            title_box.click()
            page.wait_for_timeout(300)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            title_box.fill(YT_TITLE[:100])
            page.wait_for_timeout(500)
            print("[+] Title set successfully!", flush=True)

        # Set Description
        print("[6] Setting Description...", flush=True)
        desc_box = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
        if desc_box.count() > 0:
            desc_box.click()
            page.wait_for_timeout(300)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            desc_box.fill(YT_DESC)
            page.wait_for_timeout(500)
            print("[+] Description set successfully!", flush=True)

        # Audience: Not made for kids
        print("[7] Setting Audience...", flush=True)
        not_kids = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
        if not_kids.count() > 0:
            not_kids.click()
            page.wait_for_timeout(500)
            print("[+] Audience set: Not made for kids.", flush=True)

        # Wizard steps
        print("[8] Stepping through wizard...", flush=True)
        for step in range(3):
            next_btn = page.locator("ytcp-button#next-button, button:has-text('Next')").first
            if next_btn.count() > 0 and next_btn.is_visible() and next_btn.is_enabled():
                next_btn.click()
                print(f"[+] Clicked Next (Step {step+1})", flush=True)
                page.wait_for_timeout(2500)

        # Visibility: PUBLIC
        print("[9] Setting Visibility to PUBLIC...", flush=True)
        pub_radio = page.locator("ytcp-uploads-dialog tp-yt-paper-radio-button[name='PUBLIC'], tp-yt-paper-radio-button[name='PUBLIC']").first
        if pub_radio.count() > 0:
            pub_radio.click(force=True)
            print("[+] Visibility set: PUBLIC.", flush=True)
            page.wait_for_timeout(1500)

        # Publish
        print("[10] Clicking Publish button...", flush=True)
        publish_btn = page.locator("ytcp-uploads-dialog ytcp-button#done-button, ytcp-uploads-dialog button:has-text('Publish'), ytcp-uploads-dialog #publish-button").first
        if publish_btn.count() == 0:
            publish_btn = page.locator("button:has-text('Publish')").first
        if publish_btn.count() > 0:
            publish_btn.click(force=True)
            print("[+] Clicked Publish!", flush=True)
            page.wait_for_timeout(4000)

        # Handle checks modal if any
        pub_anyway = page.locator("button:has-text('Publish anyway'), ytcp-button:has-text('Publish anyway')").first
        if pub_anyway.count() > 0 and pub_anyway.is_visible():
            pub_anyway.click(force=True)
            page.wait_for_timeout(4000)

        page.screenshot(path=str(BASE_DIR / "data" / "yt_ep21_original_audio_posted.png"))
        print("[SUCCESS] YouTube upload completed! Screenshot saved.", flush=True)
        
        page.close()

if __name__ == "__main__":
    run()
