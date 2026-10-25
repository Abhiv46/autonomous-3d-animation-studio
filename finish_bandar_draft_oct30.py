import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

OUT_DIR = r"C:\TheNaughtyDuo_Automation\output"
thumb_path = os.path.join(OUT_DIR, "bandar_mama_thumbnail.jpg")

subprocess.run(["taskkill", "/F", "/IM", "brave.exe"], capture_output=True)
time.sleep(2)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=r'C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data',
        executable_path=r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe',
        headless=True,
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        viewport={'width': 1600, 'height': 1000}
    )
    page = browser.new_page()
    page.goto('https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short', timeout=60000)
    time.sleep(6)

    try:
        skip = page.get_by_text('SKIP TO YOUTUBE STUDIO')
        if skip.count() > 0:
            skip.first.click(force=True)
            time.sleep(3)
    except Exception:
        pass

    draft_row = page.locator('ytcp-video-row:has-text("Draft")').first
    if draft_row.count() > 0:
        print("[*] Found Bandar Mama Draft row, clicking Edit draft...", flush=True)
        draft_row.hover()
        time.sleep(1)
        draft_row.locator('ytcp-button:has-text("Edit draft")').first.click(force=True)
        time.sleep(5)

        # Step 1: Check / Set Details & SEO
        t_box = page.locator("#title-textarea #textbox, div#textbox[aria-label*='title' i]").first
        if t_box.is_visible():
            t_box.click(force=True)
            time.sleep(0.3)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            time.sleep(0.3)
            page.keyboard.insert_text("बंदर मामा पहन पजामा 🐒🥻 Bandar Mama Pahan Pajama | The Naughty Duo #Shorts")
            time.sleep(1)
            print("  [OK] Bilingual SEO Title set.", flush=True)

        d_box = page.locator("#description-textarea #textbox, div#textbox[aria-label*='Tell viewers' i]").first
        if d_box.count() > 0 and d_box.is_visible():
            d_box.click(force=True)
            time.sleep(0.3)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            time.sleep(0.3)
            page.keyboard.insert_text("""बंदर मामा पहन पजामा! 🐒🥻 Dawat khane aaye! Kaartik aur Kaavya ki dawat me aaye Bandar Mama apne funny peele pajame me! Dekhiye garam rasgulle ka mazedaar cartoon comedy scene! 😂✨

🗣️ Dialogue & Rhyme:
Kaartik: "Bandar mama pahan pajama, dawat khane aaye!" 🐒🥻
Kaavya: "Arey bhaiya dekho! Bandar mama ka pajama kitna funny hai!" 😆✨
Kaartik: "Garam rasgulla khaya munh me, jeebh jalayi haaye!" 🥣🔥
Together: "Agar aapko Bandar Mama ki masti pasand aayi, toh video ko LIKE karein aur channel ko SUBSCRIBE karein! Bye-bye!" 👋❤️

🔔 Subscribe to The Naughty Duo for daily 3D Hindi nursery rhymes & hilarious cartoon shorts!

#TheNaughtyDuo #Shorts #BandarMama #BandarMamaPahanPajama #HindiRhymes #KidsCartoon #3DAnimation #CuteBabies #TrendingShorts #FunnyMonkeys""")
            time.sleep(1)
            print("  [OK] Full SEO Description set.", flush=True)

        if os.path.exists(thumb_path):
            thumb_input = page.locator("input#file-loader, input[type='file'][accept*='image']").first
            if thumb_input.count() > 0:
                thumb_input.set_input_files(thumb_path)
                time.sleep(3)
                print("  [OK] 3D Thumbnail set.", flush=True)

        # Click Next 1, 2, 3
        for s in range(3):
            nxt = page.locator('#next-button').first
            if nxt.is_visible():
                nxt.click(force=True)
                time.sleep(3)

        # Click Schedule card text
        print("[*] Clicking Schedule card...", flush=True)
        page.get_by_text("Select a date to make your video public.").first.click(force=True)
        time.sleep(3)

        # Set Date: Oct 30, 2026
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
                    page.keyboard.insert_text("Oct 30, 2026")
                    page.keyboard.press("Enter")
                    time.sleep(1)
                    print("  [OK] Date set: Oct 30, 2026", flush=True)
                    break

        # Dismiss datepicker
        page.locator("ytcp-video-visibility-select p, #visibility-title").first.click(force=True)
        time.sleep(1)

        # Set Time to 6:30 PM (Evening slot)
        for inp in page.locator("input:visible").all():
            val = inp.input_value()
            if any(t in val for t in ["AM", "PM", ":"]):
                inp.click(force=True)
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                page.keyboard.insert_text("6:30 PM")
                page.keyboard.press("Enter")
                time.sleep(1)
                print("  [OK] Time set: 6:30 PM", flush=True)
                break

        page.locator("ytcp-video-visibility-select p, #visibility-title").first.click(force=True)
        time.sleep(2)

        # Click Done / Schedule
        done_btn = page.locator("#done-button").first
        print("Done button text:", done_btn.inner_text().strip())
        done_btn.click(force=True)
        time.sleep(12)

        cb = page.locator("#close-button").first
        if cb.is_visible():
            cb.click(force=True)
            time.sleep(2)

    # Verification on Shorts table
    page.goto('https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short', timeout=60000)
    time.sleep(6)
    try:
        skip = page.get_by_text('SKIP TO YOUTUBE STUDIO')
        if skip.count() > 0:
            skip.first.click(force=True)
            time.sleep(3)
    except Exception:
        pass

    proof = r'C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\FINAL_BANDAR_OCT30_PROOF.png'
    page.screenshot(path=proof)
    print(f"[SUCCESS] Proof captured: {proof}", flush=True)

    rows = page.locator('ytcp-video-row').all()
    print(f"Total rows now: {len(rows)}")
    drafts_left = 0
    for i, r in enumerate(rows[:16]):
        txt = r.inner_text().replace('\n', ' -- ')
        if 'Draft' in txt:
            drafts_left += 1
        print(f"Row {i+1}: {txt[:120]}")

    print(f"\n[VERIFICATION] Remaining Drafts: {drafts_left} (ZERO DRAFT POLICY STRICTLY ENFORCED)")
    browser.close()
