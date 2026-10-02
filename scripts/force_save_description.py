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
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.set_viewport_size({"width": 1600, "height": 1000})

    url = f"https://studio.youtube.com/video/{VIDEO_ID}/edit"
    print(f"[*] Navigating to {url}...")
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    time.sleep(4)

    # Dismiss any dialogs
    skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
    if skip.count() > 0 and skip.is_visible():
        skip.click()
        time.sleep(2)

    # Description element in Studio edit page:
    # ytcp-mention-textbox#description-textarea div#textbox
    print("[*] Finding description box...")
    desc_box = page.locator("ytcp-mention-textbox#description-textarea div#textbox, #description-textarea #textbox, [aria-label*='description' i]").first
    if desc_box.count() > 0:
        desc_box.click()
        time.sleep(0.5)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.5)
        # Use clipboard or fill
        desc_box.fill(VIRAL_DESCRIPTION)
        time.sleep(1)
        print("[✓] Description text filled successfully!")
    else:
        print("[!] Description box not found directly!")

    # Tags
    show_more = page.locator("#toggle-button, button:has-text('Show more')").first
    if show_more.count() > 0 and show_more.is_visible():
        show_more.click()
        time.sleep(1)

    tags_input = page.locator("#tags-container input, input[aria-label='Tags'], #text-input").first
    if tags_input.count() > 0:
        print("[*] Typing tags...")
        tags_input.click()
        for t in VIRAL_TAGS:
            page.keyboard.type(t)
            page.keyboard.press("Enter")
            time.sleep(0.1)
        print("[✓] Tags entered!")

    # Check Save button
    save_btn = page.locator("ytcp-button#save, ytcp-button:has-text('Save'), #save-button").first
    print(f"Save button enabled: {save_btn.is_enabled()}")
    if save_btn.is_enabled():
        save_btn.click()
        time.sleep(4)
        print("[🎉] METADATA & DESCRIPTION SAVED!")
    else:
        print("[!] Save button disabled, attempting forced trigger...")
        page.keyboard.type(" ")
        time.sleep(0.5)
        if save_btn.is_enabled():
            save_btn.click()
            time.sleep(4)
            print("[🎉] SAVED AFTER TRIGGER!")

    page.screenshot(path="studio_after_desc_fix.png")
    browser.close()
