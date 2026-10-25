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
    "title": "कालू मदारी आया 🐻🥁 Kalu Madari Aaya | The Naughty Duo #Shorts",
    "desc": """कालू मदारी आया! 🐻🥁 Kaartik aur Kaavya ke gaon me aaya Kalu Madari apne pyaare Golu Bhalu ke saath! Dekhiye Bhalu ka masti bhara mazedaar dance aur Damru ki taal! 🥰✨

🗣️ Dialogue & Rhyme:
Madari: "Dam-dam-dam-dam damroo baaje! Kalu Madari aaya, saath me Golu Bhalu laya!" 🥁🐻
Kaavya: "Arey bhaiya dekho! Kitna pyaara Golu Bhalu aaya hai!" 👧✨
Madari: "Naach mere bhalu naach! Bachhon ko dance dikha!" 🐾💃
Kaavya: "Hahaha! Bhalu toh matak-matak ke mast naach raha hai!" 😆❤️
Kaartik & Kaavya: "Waah Bhalu bhaiya waah! Kya mast dance kiya!" 👏🌟
Kaartik & Kaavya: "Golu Bhalu ka dance pasand aaya toh LIKE aur SUBSCRIBE zaroor karna! Bye-bye!" 👋❤️

📺 Watch Our 24/7 Live Stream & Full Episodes:
https://www.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/live

🔔 Subscribe to The Naughty Duo for daily 3D Hindi cartoon rhymes & musical shorts!

#TheNaughtyDuo #Shorts #KaluMadari #BhaluKaDance #HindiRhymes #KidsCartoon #3DAnimation #CuteBabies #TrendingShorts #DancingBear""",
    "tags": "the naughty duo, kalu madari aaya, kalu madari bhalu laya, bhalu ka dance, dam dam damru baaje, hindi rhymes, kids 3d animation, chotu aur choti, nursery rhymes hindi, viral shorts, cartoon for kids, balveer rhymes, trending kids video, cartoon dance",
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

    def handle_skip():
        try:
            skip = page.get_by_text("SKIP TO YOUTUBE STUDIO")
            if skip.count() > 0:
                skip.first.click(force=True)
                time.sleep(3)
        except Exception:
            pass

    print("[*] Opening YouTube Studio Shorts table...", flush=True)
    page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", timeout=60000)
    time.sleep(6)
    handle_skip()
    time.sleep(4)

    # Find the old Kalu Madari row to delete it
    print("[*] Searching for old Kalu Madari row...", flush=True)
    rows = page.locator("ytcp-video-row").all()
    print(f"Total rows found: {len(rows)}")
    kalu_deleted = False
    for r in rows:
        txt = r.inner_text()
        if "Kalu Madari" in txt or "Bhalu" in txt:
            print(f"  [+] Found existing Kalu row. Deleting old version...", flush=True)
            r.hover()
            time.sleep(1)
            # Find options menu button (3 dots)
            opts_btn = r.locator("ytcp-icon-button#options, [aria-label*='Options' i], button[aria-label*='Options' i]").first
            if opts_btn.is_visible():
                opts_btn.click(force=True)
                time.sleep(1.5)
                del_btn = page.locator("ytcp-menu-item:has-text('Delete forever'), [role='menuitem']:has-text('Delete')").first
                if del_btn.is_visible():
                    del_btn.click(force=True)
                    time.sleep(2)
                    chk = page.locator("tp-yt-paper-checkbox, paper-checkbox#confirm-checkbox, input[type='checkbox']").first
                    if chk.is_visible():
                        chk.click(force=True)
                        time.sleep(1)
                    confirm_del = page.locator("ytcp-button#confirm-button, button:has-text('Delete forever')").first
                    if confirm_del.is_visible():
                        confirm_del.click(force=True)
                        print("  [OK] Old Kalu Madari video deleted successfully!", flush=True)
                        time.sleep(6)
                        kalu_deleted = True
                        break

    # Now upload the new pristine Dual-Audio Master Video
    print(f"\n[*] Uploading New Dual-Audio Master: {ep['video']}...", flush=True)
    page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", timeout=60000)
    time.sleep(6)
    handle_skip()
    time.sleep(3)

    create_btn = page.locator("#create-icon, button:has-text('Create'), ytcp-button:has-text('Create'), [aria-label*='Create' i]").first
    create_btn.click(force=True)
    time.sleep(2)

    upload_opt = page.locator("tp-yt-paper-item:has-text('Upload videos'), [role='menuitem']:has-text('Upload')").first
    upload_opt.click(force=True)
    time.sleep(3)

    file_input = page.locator("input[type='file']").first
    file_input.set_input_files(ep["video"])
    print("  [+] Video file attached. Waiting 18s for processing...", flush=True)
    time.sleep(18)

    # Bilingual Title
    t_box = page.locator("div#textbox[aria-label*='title' i], #title-textarea #textbox").first
    t_box.wait_for(state="attached", timeout=25000)
    t_box.click(force=True)
    time.sleep(0.3)
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    time.sleep(0.3)
    page.keyboard.insert_text(ep["title"])
    time.sleep(1)
    print("  [OK] Bilingual Title locked: " + ep["title"], flush=True)

    # SEO Description
    d_box = page.locator("div#textbox[aria-label*='Tell viewers' i], #description-textarea #textbox").first
    if d_box.count() > 0:
        d_box.click(force=True)
        time.sleep(0.3)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.3)
        page.keyboard.insert_text(ep["desc"])
        time.sleep(1)
        print("  [OK] SEO Description locked with Live Stream link.", flush=True)

    # Audience: Not made for kids
    not_mfk = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
    if not_mfk.count() > 0:
        not_mfk.click(force=True)
        time.sleep(1)
        print("  [OK] Audience set: Not Made for Kids.", flush=True)

    # Expand "Show more" for Tags, Language, Related Video
    show_more = page.locator("#toggle-button, ytcp-button:has-text('Show more'), button:has-text('SHOW MORE')").first
    if show_more.is_visible():
        show_more.click(force=True)
        time.sleep(2)
        print("  [OK] Expanded Show more.", flush=True)

    # Tags
    tags_box = page.locator("input[aria-label*='Tags' i], #tags-container input").first
    if tags_box.is_visible():
        tags_box.click(force=True)
        time.sleep(0.3)
        page.keyboard.insert_text(ep["tags"])
        page.keyboard.press("Enter")
        time.sleep(1)
        print("  [OK] Tags added.", flush=True)

    # Related video linking
    print("[*] Linking Related Video...", flush=True)
    related_btn = page.locator("ytcp-video-metadata-related-video #related-video-dropdown, button:has-text('Related video'), [aria-label*='Related video' i]").first
    if related_btn.is_visible():
        related_btn.click(force=True)
        time.sleep(3)
        # Select first video in modal
        first_rel = page.locator("ytcp-entity-card, ytcp-video-row").first
        if first_rel.is_visible():
            first_rel.click(force=True)
            time.sleep(2)
            print("  [OK] Related Video successfully linked!", flush=True)

    # Next steps (Elements, Checks)
    for s in range(3):
        nxt = page.locator("#next-button").first
        if nxt.is_visible():
            nxt.click(force=True)
            time.sleep(3)

    # Visibility / Schedule
    print("[*] Setting Visibility to Schedule...", flush=True)
    # Expand schedule section
    sched_expand = page.locator("#second-container-expand-button").first
    if sched_expand.is_visible():
        sched_expand.click(force=True)
        time.sleep(2)
    else:
        page.get_by_text("Select a date to make your video public.").first.click(force=True)
        time.sleep(2)

    # Date
    dp = page.locator("#datepicker-trigger").first
    if dp.is_visible():
        dp.click(force=True)
        time.sleep(1.5)
        for inp in page.locator("input:visible").all():
            val = inp.input_value()
            if any(y in val for y in ["2026", "2025", "Oct", "Nov"]):
                inp.click(force=True)
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                page.keyboard.insert_text(ep["sched_date"])
                page.keyboard.press("Enter")
                time.sleep(1)
                print(f"  [OK] Schedule Date set: {ep['sched_date']}", flush=True)
                break

    page.locator("ytcp-video-visibility-select p, #visibility-title").first.click(force=True)
    time.sleep(1)

    # Time
    for inp in page.locator("input:visible").all():
        val = inp.input_value()
        if any(t in val for t in ["AM", "PM", ":"]):
            inp.click(force=True)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            page.keyboard.insert_text(ep["sched_time"])
            page.keyboard.press("Enter")
            time.sleep(1)
            print(f"  [OK] Schedule Time set: {ep['sched_time']}", flush=True)
            break

    page.locator("ytcp-video-visibility-select p, #visibility-title").first.click(force=True)
    time.sleep(2)

    # Final Done / Schedule
    done_btn = page.locator("#done-button").first
    print("Done button text:", done_btn.inner_text().strip())
    done_btn.click(force=True)
    time.sleep(14)

    close_btn = page.locator("#close-button").first
    if close_btn.is_visible():
        close_btn.click(force=True)
        time.sleep(2)

    # Capture final proof
    page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", timeout=60000)
    time.sleep(6)
    handle_skip()
    time.sleep(3)

    proof = os.path.join(SCREENSHOT_DIR, "NEW_KALU_ORIGINAL_AUDIO_OCT30_SCHEDULED.png")
    page.screenshot(path=proof)
    print(f"[SUCCESS] Proof captured at: {proof}", flush=True)

    rows_final = page.locator("ytcp-video-row").all()
    print(f"Total rows in Shorts table now: {len(rows_final)}")
    for i, r in enumerate(rows_final[:6]):
        print(f"Row {i+1}: {r.inner_text().replace(chr(10), ' -- ')[:130]}")

    browser.close()
    print("\n[ALL DONE] Kalu Madari successfully replaced with Dual-Audio Master and Scheduled! 🚀🎉")
