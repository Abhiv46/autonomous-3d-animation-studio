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

VIRAL_DESCRIPTION = """Mummy ne banaye the extra teekhe Golgappe! 🌶️😋
Kaartik ne bina puche sabse bada crispy golgappa munh me daal liya... aur fir kaano se dhuwan nikal gaya! 😂
Dekhiye Kaartik ka ye hilarious teekha reaction aur Mummy ka sweet group hug! ❤️✨

Aapko teekha golgappa pasand hai ya meetha? Comment karke zaroor batayein! 👇🥰

Aise hi pyare 3D Hindi animated cartoons aur comedy stories ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔

#shorts #TheNaughtyDuo #golgappaprank #panipuri #funnycartoon #3danimation #kartikandkaavya #comedy #familycomedy #viralshorts #cartoonhindi #relatablecomedy #trendingshorts"""

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
    "comedy cartoon hindi",
    "family comedy",
    "relatable comedy shorts",
    "baccho ke cartoon"
]

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=BRAVE_DATA,
        executable_path=BRAVE_EXE,
        headless=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.set_viewport_size({"width": 1600, "height": 1000})

    url = f"https://studio.youtube.com/video/{VIDEO_ID}/edit"
    print(f"[*] Navigating to {url}...")
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    time.sleep(3)

    # 1. Click 'SKIP TO YOUTUBE STUDIO'
    skip = page.locator("button:has-text('SKIP TO YOUTUBE STUDIO'), a:has-text('SKIP TO YOUTUBE STUDIO'), span:has-text('SKIP TO YOUTUBE STUDIO')").first
    if skip.count() > 0:
        print("[*] Clicking 'SKIP TO YOUTUBE STUDIO'...")
        skip.click()
        time.sleep(4)
    else:
        # Also check simple text locator
        skip_txt = page.get_by_text("SKIP TO YOUTUBE STUDIO", exact=False).first
        if skip_txt.count() > 0:
            skip_txt.click()
            time.sleep(4)

    page.screenshot(path="studio_after_skip.png")

    # 2. Description box
    print("[*] Looking for description box...")
    desc_box = page.locator("#description-textarea #textbox, [aria-label*='description' i], [aria-label*='Tell viewers' i]").first
    if desc_box.count() > 0:
        desc_box.click()
        time.sleep(0.5)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.5)
        desc_box.fill(VIRAL_DESCRIPTION)
        print("[✓] Description text injected!")
        time.sleep(1)

    # 3. Tags
    show_more = page.locator("#toggle-button, button:has-text('Show more')").first
    if show_more.count() > 0 and show_more.is_visible():
        show_more.click()
        time.sleep(1)

    tags_input = page.locator("#tags-container input, input[aria-label='Tags'], #text-input").first
    if tags_input.count() > 0:
        print("[*] Adding tags...")
        tags_input.click()
        for t in VIRAL_TAGS:
            page.keyboard.type(t)
            page.keyboard.press("Enter")
            time.sleep(0.1)
        print("[✓] Tags entered!")

    # 4. Save button
    save_btn = page.locator("ytcp-button#save, ytcp-button:has-text('Save'), #save-button, button:has-text('Save')").first
    print("Save button enabled:", save_btn.is_enabled())
    if save_btn.is_enabled():
        save_btn.click()
        time.sleep(4)
        print("[🎉] DESCRIPTION & TAGS SAVED PERMANENTLY!")
        page.screenshot(path="studio_saved_success.png")

    browser.close()
