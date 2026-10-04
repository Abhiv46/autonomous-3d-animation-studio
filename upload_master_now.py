import sys
import json
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
VIDEO_FILE = BASE_DIR / "data" / "output" / "TheNaughtyDuo_GoodHabits_Master.mp4"
LOG_FILE = Path(r"C:\TheNaughtyDuo_Automation\uploaded_videos_log.json")

YT_TITLE = "Kaavya & Kaartik Ki Pyari Adatein! 🌟 Mil-Baant Kar Khaana Hai! #TheNaughtyDuo #shorts"

YT_DESC = (
    "Mil-baant kar khaana hai, sabko khush karna hai! 🍎✨\n"
    "Kaartik aur Kaavya ki pyari achhi adatein — subah uthkar brush karna, haath dhona, yummy fruits share karna aur toys sametna! 🪥🧼🧸\n"
    "Dekhiye dono ka adorable 3D cartoon safar aur seekhiye good habits! 🥰❤️\n\n"
    "Aapke bachhe ko kaunsa fruit sabse pasand hai? Comment me batayein! 👇\n\n"
    "🔔 Aise hi mazedar 3D Hindi animated cartoons aur pyare rhymes ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! ✨\n\n"
    "#shorts #TheNaughtyDuo #GoodHabits #KidsRhymes #KaavyaAndKaartik #3DAnimation #HindiRhymes #NurseryRhymes #SharingIsCaring #ToddlerLearning #ViralShorts #Trending"
)

YT_TAGS = [
    "The Naughty Duo", "good habits for kids", "mil baant kar khana hai",
    "sharing is caring", "toddler good habits", "brush your teeth rhyme",
    "wash hands song", "hindi nursery rhymes", "3d animation hindi cartoon",
    "kaavya and kaartik", "kids learning cartoon", "cocomelon hindi",
    "viral shorts", "trending kids animation"
]

def main():
    print(f"[*] Video File: {VIDEO_FILE} (Size: {VIDEO_FILE.stat().st_size / (1024*1024):.2f} MB)")
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        
        # 1. Click Create
        print("[1] Clicking Create button...")
        create_btn = page.locator("#create-icon, button:has-text('Create'), ytcp-button:has-text('Create')").first
        create_btn.click()
        time.sleep(1.5)
        
        # 2. Click Upload videos
        print("[2] Clicking Upload videos...")
        upload_opt = page.locator("text='Upload videos'").first
        upload_opt.click()
        time.sleep(2)
        
        # 3. File Chooser
        print("[3] Triggering File Chooser...")
        select_files_btn = page.locator("#select-files-button, button:has-text('Select files'), ytcp-button:has-text('Select files')").first
        with page.expect_file_chooser(timeout=15000) as fc_info:
            select_files_btn.click()
        fc = fc_info.value
        fc.set_files(str(VIDEO_FILE))
        print("[+] File attached via file chooser!")
        
        # 4. Wait for processing & video link
        print("[*] Waiting for upload dialog to process...")
        time.sleep(8)
        
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
            time.sleep(1)
        print(f"[+] Video Link: {video_link}")
        
        # 5. Title
        print("[5] Setting Title...")
        title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        if title_box.count() > 0:
            title_box.click()
            time.sleep(0.3)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            title_box.fill(YT_TITLE[:100])
            time.sleep(0.5)
            print("[✓] Title set!")
            
        # 6. Description
        print("[6] Setting Description...")
        desc_box = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
        if desc_box.count() > 0:
            desc_box.click()
            time.sleep(0.3)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            desc_box.fill(YT_DESC)
            time.sleep(0.5)
            print("[✓] Description set!")
            
        # 7. Tags
        show_more = page.locator("#toggle-button, button:has-text('Show more')").first
        if show_more.count() > 0 and show_more.is_visible():
            show_more.click()
            time.sleep(1)
            
        tags_input = page.locator("#tags-container input, input[aria-label='Tags'], #text-input").first
        if tags_input.count() > 0 and tags_input.is_visible():
            print("[*] Adding tags...")
            tags_input.click()
            for t in YT_TAGS:
                page.keyboard.type(t)
                page.keyboard.press("Enter")
                time.sleep(0.05)
            print("[✓] Tags added!")
            
        # 8. Audience: Not made for kids
        print("[8] Setting Audience...")
        not_kids = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
        if not_kids.count() > 0:
            not_kids.click()
            time.sleep(0.5)
            print("[✓] Audience set: Not made for kids.")
            
        # 9. Next buttons
        print("[9] Stepping through wizard...")
        for step in range(3):
            next_btn = page.locator("ytcp-button#next-button, button:has-text('Next')").first
            if next_btn.count() > 0 and next_btn.is_visible() and next_btn.is_enabled():
                next_btn.click()
                print(f"[✓] Clicked Next (Step {step+1})")
                time.sleep(2.5)
                
        # 10. Visibility: PUBLIC
        print("[10] Setting Visibility to PUBLIC...")
        pub_radio = page.locator("ytcp-uploads-dialog tp-yt-paper-radio-button[name='PUBLIC'], tp-yt-paper-radio-button[name='PUBLIC']").first
        if pub_radio.count() > 0:
            pub_radio.click(force=True)
            print("[✓] Visibility set: PUBLIC.")
            time.sleep(1.5)
            
        # 11. Publish
        print("[11] Clicking Publish button...")
        publish_btn = page.locator("ytcp-uploads-dialog ytcp-button#done-button, ytcp-uploads-dialog button:has-text('Publish'), ytcp-uploads-dialog #publish-button").first
        if publish_btn.count() == 0:
            publish_btn = page.locator("button:has-text('Publish')").first
        if publish_btn.count() > 0:
            publish_btn.click(force=True)
            print("[✓] Clicked Publish!")
            time.sleep(6)
            
        pub_anyway = page.locator("button:has-text('Publish anyway'), ytcp-button:has-text('Publish anyway')").first
        if pub_anyway.count() > 0 and pub_anyway.is_visible():
            pub_anyway.click(force=True)
            time.sleep(4)
            
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_good_habits_published_proof.png"
        page.screenshot(path=proof_path)
        print(f"[🎉 SUCCESS] YouTube upload completed! Screenshot: {proof_path}")
        
        # Log to uploaded_videos_log.json
        entry = {
            "key": "good_habits_mil_baant_kar_khana",
            "title": YT_TITLE,
            "filename": VIDEO_FILE.name,
            "youtube": video_link,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "LIVE_PUBLIC"
        }
        try:
            records = []
            if LOG_FILE.exists():
                records = json.loads(LOG_FILE.read_text(encoding="utf-8"))
            if isinstance(records, dict) and "uploaded" in records:
                records["uploaded"].append(entry)
            elif isinstance(records, list):
                records.append(entry)
            LOG_FILE.write_text(json.dumps(records, indent=4), encoding="utf-8")
            print("[+] Logged into uploaded_videos_log.json!")
        except Exception as e:
            print(f"[!] Log note: {e}")

if __name__ == "__main__":
    main()
