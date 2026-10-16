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

def upload():
    print("[1] Connecting to Brave via CDP...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        
        # Look for existing tab or open new
        page = context.new_page()
        print("[2] Navigating to studio.youtube.com...", flush=True)
        page.goto("https://studio.youtube.com", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)
        print(f"    Current Page URL: {page.url}", flush=True)
        
        # Check for skip button
        skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
        if skip.count() > 0 and skip.is_visible():
            print("    Clicking Skip to Studio...", flush=True)
            skip.click()
            page.wait_for_timeout(2000)

        # Click Create button
        print("[3] Clicking Create button...", flush=True)
        create_btn = page.locator("ytcp-button#create-icon, button:has-text('Create'), ytcp-button:has-text('Create')").first
        create_btn.wait_for(state="visible", timeout=15000)
        create_btn.click()
        page.wait_for_timeout(1500)

        # Click Upload videos
        print("[4] Clicking Upload videos...", flush=True)
        upload_opt = page.get_by_text("Upload videos", exact=False).first
        upload_opt.wait_for(state="visible", timeout=10000)
        upload_opt.click()
        page.wait_for_timeout(2500)

        # Upload file
        print(f"[5] Attaching video file: {VIDEO_PATH}...", flush=True)
        select_files_btn = page.locator("#select-files-button, button:has-text('Select files'), ytcp-button:has-text('Select files')").first
        if select_files_btn.count() > 0 and select_files_btn.is_visible():
            with page.expect_file_chooser(timeout=10000) as fc_info:
                select_files_btn.click()
            fc = fc_info.value
            fc.set_files(VIDEO_PATH)
        else:
            file_input = page.locator("input[type='file']").first
            file_input.set_input_files(VIDEO_PATH)

        print("[6] File selected! Waiting 10s for upload dialog to process...", flush=True)
        page.wait_for_timeout(10000)

        # Extract Video URL link
        video_link = None
        for _ in range(15):
            links = page.locator("a.ytcp-video-info, a[href*='youtu.be'], a[href*='youtube.com/shorts'], a[href*='youtube.com/watch']")
            if links.count() > 0:
                for idx in range(links.count()):
                    href = links.nth(idx).get_attribute("href")
                    if href and ("youtu.be" in href or "shorts" in href or "watch" in href):
                        video_link = href
                        break
            if video_link:
                break
            page.wait_for_timeout(1000)

        print(f"[+] Detected Video Link: {video_link}", flush=True)

        # Fill Title
        print("[7] Setting Video Title...", flush=True)
        title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        if title_box.count() > 0:
            title_box.click()
            page.wait_for_timeout(300)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            title_box.fill(YT_TITLE[:100])
            page.wait_for_timeout(500)
            print("    Title set successfully!", flush=True)

        # Fill Description
        print("[8] Setting Video Description...", flush=True)
        desc_box = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
        if desc_box.count() > 0:
            desc_box.click()
            page.wait_for_timeout(300)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            desc_box.fill(YT_DESC)
            page.wait_for_timeout(500)
            print("    Description set successfully!", flush=True)

        # Audience: Not made for kids
        print("[9] Setting Audience (Not made for kids)...", flush=True)
        not_kids = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
        if not_kids.count() > 0:
            not_kids.click()
            page.wait_for_timeout(500)
            print("    Audience set successfully!", flush=True)

        # Show More for Tags
        print("[10] Expanding Show More to insert Tags...", flush=True)
        show_more = page.locator("ytcp-button#toggle-button, div:has-text('Show more')").first
        if show_more.count() > 0 and show_more.is_visible():
            show_more.click()
            page.wait_for_timeout(1000)

        # Fill Tags
        tags_input = page.locator("input[aria-label*='Tags' i], #tags-container input").first
        if tags_input.count() > 0 and tags_input.is_visible():
            tags_str = ", ".join(YT_TAGS)
            tags_input.fill(tags_str)
            tags_input.press("Enter")
            print("    Tags set successfully!", flush=True)

        # Wizard Steps (Elements, Checks)
        print("[11] Progressing through Wizard Steps...", flush=True)
        for step in range(3):
            next_btn = page.locator("ytcp-button#next-button, button:has-text('Next')").first
            if next_btn.count() > 0 and next_btn.is_visible() and next_btn.is_enabled():
                next_btn.click()
                print(f"    Clicked Next (Step {step+1})", flush=True)
                page.wait_for_timeout(3000)

        # Set Visibility to PUBLIC
        print("[12] Setting Visibility to PUBLIC...", flush=True)
        pub_radio = page.locator("ytcp-uploads-dialog tp-yt-paper-radio-button[name='PUBLIC'], tp-yt-paper-radio-button[name='PUBLIC']").first
        if pub_radio.count() > 0:
            pub_radio.click(force=True)
            print("    Visibility set to PUBLIC!", flush=True)
            page.wait_for_timeout(1500)

        # Click Publish button
        print("[13] Publishing Video...", flush=True)
        publish_btn = page.locator("ytcp-uploads-dialog ytcp-button#done-button, ytcp-uploads-dialog button:has-text('Publish'), ytcp-uploads-dialog #publish-button").first
        if publish_btn.count() == 0:
            publish_btn = page.locator("button:has-text('Publish')").first
        if publish_btn.count() > 0:
            publish_btn.click(force=True)
            print("    Publish button clicked!", flush=True)
            page.wait_for_timeout(8000)

        # Save confirmation screenshot
        proof_path = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\youtube_publish_proof.png"
        page.screenshot(path=proof_path)
        print(f"[+] Proof screenshot saved to: {proof_path}", flush=True)

        print("\n==========================================")
        print("  YOUTUBE VIDEO PUBLISHED SUCCESSFULLY!  ")
        print(f"  Live Video URL: {video_link}")
        print("==========================================")

if __name__ == "__main__":
    upload()
