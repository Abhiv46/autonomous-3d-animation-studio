import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

VID_ID = "65TS-XGpBFc"
YT_TITLE = "Kaavya & Kaartik Ki Pyari Adatein! 🌟 Mil-Baant Kar Khaana Hai! #TheNaughtyDuo #shorts"

YT_DESC = """Mil-baant kar khaana hai, sabko khush karna hai! 🍎✨
Kaartik aur Kaavya ki pyari achhi adatein — subah uthkar brush karna, haath dhona, yummy fruits share karna aur toys sametna! 🪥🧼🧸
Dekhiye dono ka adorable 3D cartoon safar aur seekhiye good habits! 🥰❤️

Aapke bachhe ko kaunsa fruit sabse pasand hai? Comment me batayein! 👇

🔔 Aise hi mazedar 3D Hindi animated cartoons aur pyare rhymes ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! ✨

#shorts #TheNaughtyDuo #GoodHabits #KidsRhymes #KaavyaAndKaartik #3DAnimation #HindiRhymes #NurseryRhymes #SharingIsCaring #ToddlerLearning #ViralShorts #Trending"""

YT_TAGS = [
    "The Naughty Duo", "@TheNaughtyDuoOfficial", "good habits for kids",
    "mil baant kar khana hai", "sharing is caring", "toddler good habits",
    "brush your teeth rhyme", "wash hands song", "hindi nursery rhymes",
    "3d animation hindi cartoon", "kaavya and kaartik", "kids learning cartoon",
    "cocomelon hindi", "viral shorts 2026", "trending kids animation"
]

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    
    url = f"https://studio.youtube.com/video/{VID_ID}/edit"
    print(f"[*] Navigating to {url}...")
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    time.sleep(3)
    
    # 1. Title
    title_box = page.locator("#textbox[aria-label*='title' i], [aria-label*='Add a title' i]").first
    if title_box.count() > 0:
        title_box.click()
        time.sleep(0.3)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.3)
        title_box.fill(YT_TITLE[:100])
        time.sleep(0.5)
        print("[✓] Title updated!")
        
    # 2. Description
    desc_area = page.locator("#description-textarea div#textbox, ytcp-mention-textbox#description-textarea div#textbox").first
    if desc_area.count() > 0:
        desc_area.click()
        time.sleep(0.3)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.3)
        desc_area.fill(YT_DESC)
        time.sleep(0.5)
        print("[✓] Description updated!")
        
    # 3. Tags
    show_more = page.locator("#toggle-button, button:has-text('Show more')").first
    if show_more.count() > 0 and show_more.is_visible():
        show_more.scroll_into_view_if_needed()
        show_more.click()
        time.sleep(1)
        
    tags_input = page.locator("#tags-container input, input[aria-label='Tags'], #text-input").first
    if tags_input.count() > 0 and tags_input.is_visible():
        tags_input.scroll_into_view_if_needed()
        tags_input.click()
        for t in YT_TAGS:
            page.keyboard.type(t)
            page.keyboard.press("Enter")
            time.sleep(0.05)
        print("[✓] Tags entered!")
        
    # 4. Check Visibility
    vis_btn = page.locator(".visibility-type, ytcp-video-visibility-select, [aria-label*='visibility' i]").first
    if vis_btn.count() > 0:
        print("[*] Visibility element found, checking status...")
        vis_btn.scroll_into_view_if_needed()
        vis_btn.click()
        time.sleep(1)
        pub_radio = page.locator("tp-yt-paper-radio-button[name='PUBLIC']").first
        if pub_radio.count() > 0:
            pub_radio.click(force=True)
            print("[✓] Set to PUBLIC!")
            time.sleep(0.5)
            # Click Save on popup
            done_vis = page.locator("#save-button, button:has-text('Save'), button:has-text('Done')").first
            if done_vis.count() > 0:
                done_vis.click(force=True)
                time.sleep(1)
                
    # 5. Save main page
    save_btn = page.locator("ytcp-button#save, ytcp-button:has-text('Save'), #save-button").first
    if save_btn.count() > 0 and save_btn.is_enabled():
        save_btn.click()
        time.sleep(4)
        print("[🎉 SUCCESS] Good Habits Video saved & published PUBLIC!")
    else:
        print("[i] Save button already saved or not enabled.")
        
    proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\good_habits_final_public_proof.png"
    page.screenshot(path=proof)
    print("Screenshot saved to:", proof)
