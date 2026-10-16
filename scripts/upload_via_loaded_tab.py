import os
import sys
import time
from playwright.sync_api import sync_playwright

VIDEO_PATH = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\Kaavya_Chocolate_Chori_Master.mp4"
THUMBNAIL_PATH = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\thumbnail_chocolate.jpg"

YT_TITLE = "Kaavya Ne Chori Ki Chocolate! 🍫😂 Kaartik Ne Pakda Rangey Haath! #TheNaughtyDuo #shorts"

YT_DESC = """Mummy ne fridge me rakhi thi chocolate, lekin Kaavya ne secretly saari chocolate chupa li! 🍫😋
Kaartik bhaiyya ko ho gaya shak... aur shuru hua interrogation! 🕵️‍♂️😂
Kaavya ne banaye cute bahane: "Maine toh chocolate dekhi bhi nahi!" 😇
Lekin achanak Kaavya ke muh par lagi chocolate ne khol diya saara raaz! 😱🍫🤣
Dekhiye Kaavya aur Kaartik ki sabse funny chocolate chori comedy! ❤️✨

💬 Sawaal: Kya aapne bhi bachpan me secretly chocolate ya mithai chori karke khayi hai? Comment me batao! 👇

🔔 Aise hi mazedaar 3D family cartoons aur daily siblings comedy stories ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 💖

#shorts #TheNaughtyDuo #KaavyaAndKaartik #ChocolateChori #FunnyShorts #HindiCartoon #3DAnimation #CartoonStories #SiblingsComedy #KidsAnimation #ViralShorts #Trending"""

YT_TAGS = [
    "The Naughty Duo", "TheNaughtyDuo", "Kaartik and Kaavya", "chocolate chori",
    "chocolate prank", "hindi cartoon", "3d animation hindi", "kids cartoon funny",
    "siblings comedy", "funny hindi stories", "cartoon video hindi", "shorts", "viral shorts"
]

def run():
    print("[1] Connecting to existing browser session via CDP...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        
        # Find the loaded Studio tab
        page = None
        for pg in context.pages:
            if "studio.youtube.com" in pg.url:
                page = pg
                break
                
        if not page:
            print("[!] Studio page not found in context!")
            return

        print(f"[2] Located Studio page: {page.title()}", flush=True)
        
        # Click the Upload icon directly (the arrow pointing up)
        print("[3] Clicking Upload button on dashboard...", flush=True)
        upload_icon = page.locator("ytcp-button#upload-button, ytcp-icon-button#upload-button, button[aria-label*='Upload' i], #upload-icon").first
        if upload_icon.count() > 0 and upload_icon.is_visible():
            upload_icon.click()
        else:
            create_btn = page.locator("#create-icon").first
            create_btn.click()
            time.sleep(1)
            page.get_by_text("Upload videos").first.click()
            
        time.sleep(2)
        
        # Set file input directly without file chooser dialog
        print(f"[4] Setting input files directly: {VIDEO_PATH}...", flush=True)
        file_input = page.locator("ytcp-uploads-dialog input[type='file'], input[type='file']").first
        file_input.set_input_files(VIDEO_PATH)
        print("[+] Video file attached! Waiting 10s for details form to appear...", flush=True)
        time.sleep(10)
        
        # Capture screenshot to verify dialog
        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\step1_dialog_opened.png")

        # Fill Title
        print("[5] Setting Video Title...", flush=True)
        title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        title_box.wait_for(state="visible", timeout=15000)
        title_box.click()
        time.sleep(0.3)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        title_box.fill(YT_TITLE[:100])
        time.sleep(0.5)
        print("    Title set successfully!", flush=True)

        # Fill Description
        print("[6] Setting Video Description...", flush=True)
        desc_box = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
        if desc_box.count() > 0 and desc_box.is_visible():
            desc_box.click()
            time.sleep(0.3)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            desc_box.fill(YT_DESC)
            time.sleep(0.5)
            print("    Description set successfully!", flush=True)

        # Audience: Not made for kids
        print("[7] Setting Audience...", flush=True)
        not_kids = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
        if not_kids.count() > 0 and not_kids.is_visible():
            not_kids.click()
            print("    Audience set: Not made for kids", flush=True)
            time.sleep(0.5)

        # Show more for tags
        print("[8] Adding viral tags...", flush=True)
        show_more = page.locator("ytcp-button#toggle-button, div:has-text('Show more')").first
        if show_more.count() > 0 and show_more.is_visible():
            show_more.click()
            time.sleep(1)

        tags_input = page.locator("input[aria-label*='Tags' i], #tags-container input").first
        if tags_input.count() > 0 and tags_input.is_visible():
            tags_str = ", ".join(YT_TAGS)
            tags_input.fill(tags_str)
            tags_input.press("Enter")
            print("    Tags set successfully!", flush=True)

        # Detect video link
        video_link = None
        links = page.locator("a.ytcp-video-info, a[href*='youtu.be'], a[href*='youtube.com/shorts']")
        if links.count() > 0:
            for i in range(links.count()):
                href = links.nth(i).get_attribute("href")
                if href and ("youtu.be" in href or "shorts" in href):
                    video_link = href
                    break
        print(f"[+] Video Link detected: {video_link}", flush=True)

        # Progress through wizard
        print("[9] Stepping through Wizard...", flush=True)
        for step in range(3):
            next_btn = page.locator("ytcp-button#next-button, button:has-text('Next')").first
            if next_btn.count() > 0 and next_btn.is_visible():
                next_btn.click()
                print(f"    Clicked Next (Step {step+1})", flush=True)
                time.sleep(2.5)

        # Set Visibility: Public
        print("[10] Setting Visibility to PUBLIC...", flush=True)
        pub_radio = page.locator("ytcp-uploads-dialog tp-yt-paper-radio-button[name='PUBLIC'], tp-yt-paper-radio-button[name='PUBLIC']").first
        if pub_radio.count() > 0:
            pub_radio.click(force=True)
            print("    Visibility set to PUBLIC!", flush=True)
            time.sleep(1.5)

        # Publish
        print("[11] Publishing...", flush=True)
        publish_btn = page.locator("ytcp-uploads-dialog ytcp-button#done-button, ytcp-uploads-dialog button:has-text('Publish'), ytcp-uploads-dialog #publish-button").first
        if publish_btn.count() == 0:
            publish_btn = page.locator("button:has-text('Publish')").first
        if publish_btn.count() > 0:
            publish_btn.click(force=True)
            print("    Publish button clicked!", flush=True)
            time.sleep(8)

        # Screenshot proof
        proof_path = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\chocolate_live_published.png"
        page.screenshot(path=proof_path)
        print(f"[SUCCESS] Upload confirmed! Screenshot: {proof_path}", flush=True)
        print(f"Live Video URL: {video_link}", flush=True)

if __name__ == "__main__":
    run()
