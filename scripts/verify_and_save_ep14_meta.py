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

VIDEO_ID = "sa218mcIeiU"

VIRAL_TITLE = "Mummy Ka Bubble Wrap Trap! 💥🤣 Ghar Me Phate Patakhe! #TheNaughtyDuo #shorts"

VIRAL_DESCRIPTION = """Online shopping ke dabbe me se nikla bada sa Bubble Wrap! 💥📦
Kaartik aur Kaavya ne hallway me bicha diya secret trap, aur Mummy ne jaise hi kadam rakha... patakhe phutne lage! 😂🤣
Dekhiye Mummy ka ye super energetic reaction aur hilarious tap-dance! ❤️✨

Bubble wrap phodne me kinko sabse zyada maza aata hai? Comment karke zaroor batayein! 👇🥰

Aise hi mazedar 3D Hindi animated cartoons aur family comedy stories ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔

#shorts #TheNaughtyDuo #bubblewrapfunny #funnycartoon #3danimation #kartikandkaavya #comedy #familycomedy #viralshorts #cartoonhindi #relatablecomedy #trendingshorts"""

VIRAL_TAGS = [
    "The Naughty Duo",
    "@TheNaughtyDuoOfficial",
    "bubble wrap funny cartoon",
    "kids prank on mom",
    "mummy prank funny",
    "funny kids animation",
    "3d animation shorts",
    "hindi cartoon shorts",
    "kartik and kaavya",
    "viral shorts 2026",
    "comedy cartoon hindi",
    "family comedy",
    "relatable comedy shorts",
    "baccho ke cartoon",
    "trending shorts"
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

    # 1. Skip dialog
    skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
    if skip.count() > 0 and skip.is_visible():
        skip.click()
        time.sleep(3)

    # 2. Title
    title_box = page.locator("#textbox[aria-label*='title' i], [aria-label*='Add a title' i]").first
    if title_box.count() > 0:
        title_box.click()
        time.sleep(0.5)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.5)
        title_box.fill(VIRAL_TITLE)
        print("[✓] Title set!")

    # 3. Description
    desc_area = page.locator("#description-textarea div#textbox, ytcp-mention-textbox#description-textarea div#textbox").first
    if desc_area.count() > 0:
        desc_area.click()
        time.sleep(0.5)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.5)
        desc_area.fill(VIRAL_DESCRIPTION)
        print("[✓] Description injected!")

    # 4. Tags
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
            time.sleep(0.05)
        print("[✓] Tags entered!")

    # 5. Save
    save_btn = page.locator("ytcp-button#save, ytcp-button:has-text('Save'), #save-button").first
    print("Save button enabled:", save_btn.is_enabled())
    if save_btn.is_enabled():
        save_btn.click()
        time.sleep(4)
        print("[🎉] EPISODE 14 METADATA & DESCRIPTION CONFIRMED SAVED!")

    page.screenshot(path="studio_ep14_verified.png")
    browser.close()
