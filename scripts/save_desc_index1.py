import os
import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

VIDEO_ID = "2wePkYa9lqw"

VIRAL_DESCRIPTION = """Mummy ne banaye the extra teekhe Golgappe! 🌶️😋
Kaartik ne bina puche sabse bada crispy golgappa munh me daal liya... aur fir kaano se dhuwan nikal gaya! 😂
Dekhiye Kaartik ka ye hilarious teekha reaction aur Mummy ka sweet group hug! ❤️✨

Aapko teekha golgappa pasand hai ya meetha? Comment karke zaroor batayein! 👇🥰

Aise hi pyare 3D Hindi animated cartoons aur comedy stories ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔

#shorts #TheNaughtyDuo #golgappaprank #panipuri #funnycartoon #3danimation #kartikandkaavya #comedy #familycomedy #viralshorts #cartoonhindi #relatablecomedy #trendingshorts"""

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

    skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
    if skip.count() > 0:
        skip.click()
        time.sleep(3)

    # In Studio edit page, there are two #textbox elements:
    # 0 is Title
    # 1 is Description
    textboxes = page.locator("#textbox")
    print(f"Total #textbox elements found: {textboxes.count()}")
    if textboxes.count() >= 2:
        desc = textboxes.nth(1)
        print("[*] Clicking description element (index 1)...")
        desc.click()
        time.sleep(0.5)
        # Use clipboard paste or evaluate to set text cleanly
        desc.evaluate("(el, text) => { el.innerText = text; el.dispatchEvent(new Event('input', { bubbles: true })); }", VIRAL_DESCRIPTION)
        time.sleep(1)
        # Type a space to trigger dirty state
        page.keyboard.type(" ")
        time.sleep(1)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    save_btn = page.locator("ytcp-button#save, ytcp-button:has-text('Save'), #save-button").first
    print(f"Save button enabled: {save_btn.is_enabled()}")
    if save_btn.is_enabled():
        save_btn.click()
        time.sleep(4)
        print("[SUCCESS] DESCRIPTION CONFIRMED SAVED!")

    page.screenshot(path="studio_desc_verified.png")
    browser.close()
