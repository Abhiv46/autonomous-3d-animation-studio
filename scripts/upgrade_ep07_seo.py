import os
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

VIDEO_ID = "2wePkYa9lqw"

VIRAL_TITLE = "Mummy Ka Spicy Golgappa Prank! 🌶️😵 Mirchi Lag Gayi! #TheNaughtyDuo #shorts"

VIRAL_DESCRIPTION = """Mummy ne banaye the extra teekhe Golgappe! 🌶️😋
Kaartik ne bina puche sabse bada crispy golgappa munh me daal liya... aur fir kaano se dhuwan nikal gaya! 😂
Dekhiye Kaartik ka ye hilarious teekha reaction aur Mummy ka sweet group hug! ❤️✨

Aapko teekha golgappa pasand hai ya meetha? Comment karke zaroor batayein! 👇🥰

Aise hi pyare 3D Hindi animated cartoons aur comedy stories ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔

#shorts #TheNaughtyDuo #golgappaprank #panipuri #funnycartoon #3danimation #kartikandkaavya #comedy #familycomedy #viralshorts #cartoonhindi #cocomelonhindi #relatablecomedy #trendingshorts"""

VIRAL_TAGS = [
    "The Naughty Duo",
    "@TheNaughtyDuoOfficial",
    "spicy golgappa prank",
    "pani puri funny cartoon",
    "mummy ka prank",
    "funny kids animation",
    "3d animation shorts",
    "hindi cartoon shorts",
    "kartik and kaavya",
    "viral shorts 2026",
    "cocomelon hindi",
    "comedy cartoon hindi",
    "family comedy",
    "relatable comedy shorts",
    "baccho ke cartoon"
]

def main():
    print("=" * 60)
    print(f"  UPGRADING SEO & TAGS FOR: https://youtube.com/shorts/{VIDEO_ID}")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        url = f"https://studio.youtube.com/video/{VIDEO_ID}/edit"
        print(f"[*] Navigating to {url}...")
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)

        # Skip dialog if present
        skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
        if skip.count() > 0 and skip.is_visible():
            skip.click()
            page.wait_for_timeout(2000)

        # 1. Title
        title_box = page.locator("#textbox[aria-label*='title' i], [aria-label*='Add a title' i]").first
        if title_box.count() > 0:
            title_box.click()
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            title_box.fill(VIRAL_TITLE)
            print("[✓] Title optimized!")
            page.wait_for_timeout(500)

        # 2. Description
        desc_box = page.locator("#description-textarea #textbox, [aria-label*='Tell viewers' i]").first
        if desc_box.count() > 0:
            desc_box.click()
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            desc_box.fill(VIRAL_DESCRIPTION)
            print("[✓] High-ranking Description optimized with rich hashtags!")
            page.wait_for_timeout(500)

        # 3. Show More for Tags
        show_more = page.locator("#toggle-button, button:has-text('Show more')").first
        if show_more.count() > 0 and show_more.is_visible():
            show_more.click()
            page.wait_for_timeout(1000)

        tags_input = page.locator("#tags-container input, input[aria-label='Tags']").first
        if tags_input.count() > 0:
            print("[*] Injecting Viral High-Search-Volume Tags...")
            tags_input.click()
            for t in VIRAL_TAGS:
                page.keyboard.type(t)
                page.keyboard.press("Enter")
                time.sleep(0.1)
            print("[✓] 15 Viral Tags injected!")

        # 4. Save Changes
        top_save = page.locator("ytcp-button#save, ytcp-button:has-text('Save'), #save-button").first
        if top_save.count() > 0 and top_save.is_enabled():
            top_save.click()
            page.wait_for_timeout(4000)
            print("[🚀 SUPREME SEO SAVED SUCCESSFULLY!]")
        else:
            print("[*] Save button was already up to date or saved.")

        browser.close()

if __name__ == "__main__":
    main()
