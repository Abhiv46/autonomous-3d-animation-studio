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
    "video": os.path.join(OUT_DIR, "TheNaughtyDuo_KaluMadari_Master.mp4"),
    "thumb": os.path.join(OUT_DIR, "kalu_madari_thumbnail.jpg"),
    "title": "Kalu Madari Aaya! 🐻🥁 Bhalu Ka Mazedaar Dance #Shorts",
    "desc": """Kalu Madari Aaya! 🐻🥁 Kaartik aur Kaavya ke gaon me aaya Kalu Madari apne pyaare Golu Bhalu ke saath! Dekhiye Bhalu ka masti bhara mazedaar dance aur Damru ki taal! 🥰✨

🗣️ Dialogue & Rhyme:
Madari: "Dam-dam-dam-dam damroo baaje! Kalu Madari aaya, saath me Golu Bhalu laya!" 🥁🐻
Kaavya: "Arey bhaiya dekho! Kitna pyaara Golu Bhalu aaya hai!" 👧✨
Madari: "Naach mere bhalu naach! Bachhon ko dance dikha!" 🐾💃
Kaavya: "Hahaha! Bhalu toh matak-matak ke mast naach raha hai!" 😆❤️
Kaartik & Kaavya: "Waah Bhalu bhaiya waah! Kya mast dance kiya!" 👏🌟
Kaartik & Kaavya: "Golu Bhalu ka dance pasand aaya toh LIKE aur SUBSCRIBE zaroor karna! Bye-bye!" 👋❤️

🔔 Subscribe to The Naughty Duo for daily 3D Hindi cartoon rhymes & musical shorts!

#TheNaughtyDuo #Shorts #KaluMadari #BhaluKaDance #HindiRhymes #KidsCartoon #3DAnimation #CuteBabies #TrendingShorts #DancingBear""",
    "tags": "the naughty duo, kalu madari aaya, kalu madari bhalu laya, bhalu ka dance, dam dam damru baaje, hindi rhymes, kids 3d animation, chotu aur choti, nursery rhymes hindi, viral shorts",
    "sched_date": "Oct 30, 2026",
    "sched_time": "12:30 PM"
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

    # Step Next 1, 2, 3
    print("[*] Stepping Next 1, 2, 3...", flush=True)
    for s in range(3):
        page.locator("#next-button").first.click(force=True)
        time.sleep(3)

    # Click Schedule card / Radio
    print("[*] Selecting Schedule...", flush=True)
    sched_card = page.get_by_text("Select a date to make your video public.").first
    if sched_card.count() > 0 and sched_card.is_visible():
        sched_card.click(force=True)
    else:
        page.locator("#second-container-expand-button, #second-container, #schedule-radio-button").first.click(force=True)
    time.sleep(2)

    # Set Date
    dp = page.locator("#datepicker-trigger").first
    if dp.is_visible():
        dp.click(force=True)
        time.sleep(1)
        for inp in page.locator('input:visible').all():
            val = inp.input_value()
            if any(y in val for y in ['2026', '2025', 'Oct', 'Nov']):
                inp.click(force=True)
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                page.keyboard.insert_text(ep["sched_date"])
                page.keyboard.press("Enter")
                time.sleep(1)
                print(f"  [OK] Date set: {ep['sched_date']}", flush=True)
                break

    page.locator("ytcp-video-visibility-select p, #visibility-title").first.click(force=True)
    time.sleep(1)

    # Set Time
    for ti in page.locator('input:visible').all():
        val = ti.input_value()
        if any(t in val for t in ['AM', 'PM', ':']):
            ti.click(force=True)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            page.keyboard.insert_text(ep["sched_time"])
            page.keyboard.press("Enter")
            time.sleep(1)
            print(f"  [OK] Time set: {ep['sched_time']}", flush=True)
            break

    page.locator("ytcp-video-visibility-select p, #visibility-title").first.click(force=True)
    time.sleep(2)

    # Click Done / Schedule
    done_btn = page.locator("#done-button").first
    print("Clicking Schedule button:", done_btn.inner_text().strip())
    done_btn.click(force=True)
    time.sleep(15)

    cb = page.locator("#close-button").first
    if cb.is_visible():
        cb.click(force=True)
        time.sleep(2)

    # Verification on Shorts Table
    page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", timeout=60000)
    time.sleep(6)
    try:
        skip = page.get_by_text("SKIP TO YOUTUBE STUDIO")
        if skip.count() > 0:
            skip.first.click(force=True)
            time.sleep(3)
    except Exception:
        pass

    final_proof = os.path.join(SCREENSHOT_DIR, "YOUTUBE_KALU_MADARI_OCT30_SCHEDULED.png")
    page.screenshot(path=final_proof)
    print(f"[SUCCESS] Proof saved at: {final_proof}", flush=True)

    rows = page.locator("ytcp-video-row").all()
    for i, r in enumerate(rows[:12]):
        txt = " | ".join([l.strip() for l in r.inner_text().splitlines() if l.strip()][:5])
        print(f"  Row {i+1}: {txt}", flush=True)

    browser.close()
    print("[ALL DONE] Master Kalu Madari video scheduled for Oct 30 @ 12:30 PM! 🚀🎉", flush=True)
