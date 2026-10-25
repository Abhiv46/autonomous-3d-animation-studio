import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
SCREENSHOT_DIR = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2"
OUT_DIR = r"C:\TheNaughtyDuo_Automation\output"

ep = {
    "video": os.path.join(OUT_DIR, "TheNaughtyDuo_BandarMama_Master.mp4"),
    "thumb": os.path.join(OUT_DIR, "bandar_mama_thumbnail.jpg"),
    "title": "बंदर मामा पहन पजामा 🐒🥻 Bandar Mama Pahan Pajama | The Naughty Duo #Shorts",
    "desc": """बंदर मामा पहन पजामा! 🐒🥻 Dawat khane aaye! Kaartik aur Kaavya ki dawat me aaye Bandar Mama apne funny peele pajame me! Dekhiye garam rasgulle ka mazedaar cartoon comedy scene! 😂✨

🗣️ Dialogue & Rhyme:
Kaartik: "Bandar mama pahan pajama, dawat khane aaye!" 🐒🥻
Kaavya: "Arey bhaiya dekho! Bandar mama ka pajama kitna funny hai!" 😆✨
Kaartik: "Garam rasgulla khaya munh me, jeebh jalayi haaye!" 🥣🔥
Together: "Agar aapko Bandar Mama ki masti pasand aayi, toh video ko LIKE karein aur channel ko SUBSCRIBE karein! Bye-bye!" 👋❤️

🔔 Subscribe to The Naughty Duo for daily 3D Hindi nursery rhymes & hilarious cartoon shorts!

#TheNaughtyDuo #Shorts #BandarMama #BandarMamaPahanPajama #HindiRhymes #KidsCartoon #3DAnimation #CuteBabies #TrendingShorts #FunnyMonkeys""",
    "tags": "the naughty duo, bandar mama pahan pajama, dawat khane aaye, garam rasgulla khaya munh me, hindi rhymes, kids 3d animation, nursery rhymes hindi, chotu aur choti, viral shorts",
    "sched_date": "Oct 30, 2026",
    "sched_time": "6:30 PM"
}

subprocess.run(["taskkill", "/F", "/IM", "brave.exe"], capture_output=True)
time.sleep(2)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=BRAVE_DATA,
        executable_path=BRAVE_EXE,
        headless=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        viewport={"width": 1600, "height": 1000},
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = browser.new_page()

    print("[*] Navigating to Shorts table...", flush=True)
    page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", timeout=60000)
    time.sleep(6)

    try:
        skip = page.get_by_text("SKIP TO YOUTUBE STUDIO")
        if skip.count() > 0:
            skip.first.click(force=True)
            time.sleep(3)
    except Exception:
        pass

    # Upload
    print(f"[*] Uploading: {ep['video']}...", flush=True)
    create_btn = page.locator("#create-icon, button:has-text('Create'), ytcp-button:has-text('Create'), [aria-label*='Create' i]").first
    create_btn.click(force=True)
    time.sleep(2)

    upload_opt = page.locator("tp-yt-paper-item:has-text('Upload videos'), [role='menuitem']:has-text('Upload')").first
    upload_opt.click(force=True)
    time.sleep(3)

    file_input = page.locator("input[type='file']").first
    file_input.set_input_files(ep["video"])
    print("  [+] Video file attached. Waiting 15s...", flush=True)
    time.sleep(15)

    # Title
    t_box = page.locator("div#textbox[aria-label*='title' i], #title-textarea #textbox").first
    t_box.wait_for(state="attached", timeout=25000)
    t_box.click(force=True)
    time.sleep(0.3)
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    time.sleep(0.3)
    page.keyboard.insert_text(ep["title"])
    time.sleep(1)
    print("  [OK] Title locked.")

    # Description
    d_box = page.locator("div#textbox[aria-label*='Tell viewers' i], #description-textarea #textbox").first
    if d_box.count() > 0:
        d_box.click(force=True)
        time.sleep(0.3)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.3)
        page.keyboard.insert_text(ep["desc"])
        time.sleep(1)
        print("  [OK] Description locked.")

    # Thumbnail
    if os.path.exists(ep["thumb"]):
        thumb_input = page.locator("input#file-loader, input[type='file'][accept*='image']").first
        if thumb_input.count() > 0:
            thumb_input.set_input_files(ep["thumb"])
            time.sleep(3)
            print("  [OK] 3D Thumbnail uploaded.")

    # Audience
    not_for_kids = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
    if not_for_kids.count() > 0:
        not_for_kids.scroll_into_view_if_needed()
        not_for_kids.click(force=True)
        time.sleep(1)
        print("  [OK] Audience set.")

    # Show More (Tags & Language)
    show_more = page.locator("#toggle-button:has-text('Show more')").first
    if show_more.count() > 0:
        show_more.scroll_into_view_if_needed()
        show_more.click(force=True)
        time.sleep(1.5)

        tags_box = page.locator("#tags-container input").first
        if tags_box.count() > 0:
            tags_box.scroll_into_view_if_needed()
            tags_box.click(force=True)
            tags_box.fill(ep["tags"])
            page.keyboard.press("Enter")
            time.sleep(1)
            print("  [OK] Tags set.")

        lang_drop = page.locator("#language-input, ytcp-form-language-input").first
        if lang_drop.count() > 0:
            lang_drop.scroll_into_view_if_needed()
            lang_drop.click(force=True)
            time.sleep(1.5)
            hindi_opt = page.locator("tp-yt-paper-item:has-text('Hindi'), [role='option']:has-text('Hindi')").first
            if hindi_opt.count() > 0:
                hindi_opt.click(force=True)
                time.sleep(1)
                print("  [OK] Language set to Hindi.")

    # Close dialog so it saves cleanly as draft, then finish_draft will schedule it
    close_dialog = page.locator("#close-button").first
    if close_dialog.is_visible():
        close_dialog.click(force=True)
        time.sleep(3)

    browser.close()
    print("[ALL DONE] Video saved to Studio! Now scheduling draft...", flush=True)
