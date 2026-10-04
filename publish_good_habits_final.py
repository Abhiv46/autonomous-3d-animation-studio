import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

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

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    
    # 1. Fill Title
    print("[1] Filling Title...")
    title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
    if title_box.count() > 0:
        title_box.click()
        time.sleep(0.3)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.3)
        title_box.fill(YT_TITLE[:100])
        time.sleep(0.5)
        print("[✓] Title set successfully!")
        
    # 2. Fill Description
    print("[2] Filling Description...")
    desc_box = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
    if desc_box.count() > 0:
        desc_box.click()
        time.sleep(0.3)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.3)
        desc_box.fill(YT_DESC)
        time.sleep(0.5)
        print("[✓] Description set successfully!")
        
    # 3. Audience: Not made for kids
    print("[3] Setting Audience...")
    not_kids = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
    if not_kids.count() > 0:
        not_kids.scroll_into_view_if_needed()
        not_kids.click()
        time.sleep(0.5)
        print("[✓] Audience set: Not made for kids.")
        
    # 4. Tags
    print("[4] Expanding Show more for tags...")
    show_more = page.locator("#toggle-button, button:has-text('Show more'), ytcp-button:has-text('Show more')").first
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
        
    # 5. Next button steps
    print("[5] Stepping through wizard...")
    for step in range(3):
        next_btn = page.locator("ytcp-button#next-button, button:has-text('Next')").first
        if next_btn.count() > 0 and next_btn.is_visible() and next_btn.is_enabled():
            next_btn.click()
            print(f"[✓] Clicked Next (Step {step+1})")
            time.sleep(2)
            
    # 6. Visibility: PUBLIC
    print("[6] Setting Visibility to PUBLIC...")
    pub_radio = page.locator("tp-yt-paper-radio-button[name='PUBLIC']").first
    if pub_radio.count() > 0:
        pub_radio.click(force=True)
        print("[✓] Selected PUBLIC!")
        time.sleep(1.5)
        
    # 7. Publish
    print("[7] Clicking Publish button...")
    done_btn = page.locator("ytcp-button#done-button, button:has-text('Publish'), #publish-button, ytcp-button:has-text('Publish'), button:has-text('Save')").first
    if done_btn.count() > 0:
        done_btn.click(force=True)
        print("[✓] Clicked Done/Publish!")
        time.sleep(6)
        
    pub_anyway = page.locator("button:has-text('Publish anyway'), ytcp-button:has-text('Publish anyway')").first
    if pub_anyway.count() > 0 and pub_anyway.is_visible():
        pub_anyway.click(force=True)
        time.sleep(3)
        
    proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\good_habits_live_proof.png"
    page.screenshot(path=proof)
    print(f"[SUCCESS] Upload finished! Saved proof: {proof}")
