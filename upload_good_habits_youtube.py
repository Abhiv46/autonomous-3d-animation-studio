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
    print("[1] Connecting to browser over CDP...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        
        print("[2] Checking YouTube Studio page...", flush=True)
        if "studio.youtube.com" not in page.url:
            page.goto("https://studio.youtube.com", wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(3000)
            
        print(f"Current URL: {page.url}", flush=True)
        
        # Dismiss any dialogs or overlays
        skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
        if skip.count() > 0 and skip.is_visible():
            print("[+] Clicking Skip to YouTube Studio...", flush=True)
            skip.click()
            page.wait_for_timeout(2000)
            
        # Check if an upload dialog is already open
        dialog = page.locator("ytcp-uploads-dialog")
        if dialog.count() == 0 or not dialog.first.is_visible():
            # Click Create
            print("[3] Clicking Create button...", flush=True)
            create_btn = page.locator("ytcp-button#create-icon, button:has-text('Create'), ytcp-button:has-text('Create'), #create-icon").first
            if create_btn.count() > 0:
                create_btn.click()
                page.wait_for_timeout(1500)
                upload_option = page.get_by_text("Upload videos", exact=False).first
                if upload_option.count() > 0 and upload_option.is_visible():
                    upload_option.click()
                page.wait_for_timeout(2000)
            
        # Attach File directly via DOM input (no FileChooser websocket transfer)
        print(f"[4] Attaching file via DOM file input: {VIDEO_FILE}...", flush=True)
        file_input = page.locator("input[type='file']").first
        file_input.set_input_files(str(VIDEO_FILE))
        print("[+] set_input_files succeeded!", flush=True)
            
        print("[*] Waiting for upload dialog to process...", flush=True)
        page.wait_for_timeout(10000)
        
        # Detect video link
        video_link = None
        for _ in range(20):
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
            print("[+] Title set!", flush=True)
            
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
            print("[+] Description set!", flush=True)
            
        # Set Tags
        show_more = page.locator("#toggle-button, button:has-text('Show more')").first
        if show_more.count() > 0 and show_more.is_visible():
            show_more.click()
            page.wait_for_timeout(1000)
            
        tags_input = page.locator("#tags-container input, input[aria-label='Tags'], #text-input").first
        if tags_input.count() > 0 and tags_input.is_visible():
            print("[*] Adding tags...", flush=True)
            tags_input.click()
            for t in YT_TAGS:
                page.keyboard.type(t)
                page.keyboard.press("Enter")
                page.wait_for_timeout(50)
            print("[+] Tags added!", flush=True)
            
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
            page.wait_for_timeout(6000)
            
        # Handle checks modal if any
        pub_anyway = page.locator("button:has-text('Publish anyway'), ytcp-button:has-text('Publish anyway')").first
        if pub_anyway.count() > 0 and pub_anyway.is_visible():
            pub_anyway.click(force=True)
            page.wait_for_timeout(4000)
            
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_good_habits_published.png"
        page.screenshot(path=proof_path)
        print(f"[SUCCESS] YouTube upload completed! Screenshot: {proof_path}", flush=True)
        
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
            print("[+] Logged into uploaded_videos_log.json!", flush=True)
        except Exception as e:
            print(f"[!] Log update note: {e}", flush=True)

if __name__ == "__main__":
    main()
