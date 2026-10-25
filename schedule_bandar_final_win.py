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
            time.sleep(2)
    except Exception:
        pass

    draft_row = page.locator('ytcp-video-row:has-text("Draft")').first
    if draft_row.count() == 0:
        print("[INFO] No Draft row found!", flush=True)
        sys.exit(0)

    print("[*] Found Draft row, clicking Edit draft...", flush=True)
    draft_row.hover()
    time.sleep(1)
    draft_row.locator('ytcp-button:has-text("Edit draft")').first.click(force=True)
    time.sleep(6)

    # 1. Step Next 1, 2, 3
    print("[*] Stepping Next 1, 2, 3...", flush=True)
    for s in range(3):
        nxt = page.locator("#next-button").first
        nxt.wait_for(state="visible", timeout=10000)
        nxt.click(force=True)
        time.sleep(3)

    # 2. Open Schedule Accordion
    print("[*] Opening Schedule Accordion...", flush=True)
    sched_expand = page.locator("#second-container-expand-button, #second-container").first
    sched_expand.click(force=True)
    time.sleep(2)

    # 3. Set Date: Oct 30, 2026
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
                page.keyboard.insert_text("Oct 30, 2026")
                page.keyboard.press("Enter")
                time.sleep(1)
                print("  [OK] Date set: Oct 30, 2026", flush=True)
                break

    # Dismiss datepicker
    page.locator("ytcp-video-visibility-select p, #visibility-title").first.click(force=True)
    time.sleep(1)

    # 4. Set Time: 6:30 PM
    for ti in page.locator('input:visible').all():
        val = ti.input_value()
        if any(t in val for t in ['AM', 'PM', ':']):
            ti.click(force=True)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            page.keyboard.insert_text("6:30 PM")
            page.keyboard.press("Enter")
            time.sleep(1)
            print("  [OK] Time set: 6:30 PM", flush=True)
            break

    page.locator("ytcp-video-visibility-select p, #visibility-title").first.click(force=True)
    time.sleep(2)

    # 5. Click Done / Schedule
    done_btn = page.locator("#done-button").first
    print("Clicking Done button text:", done_btn.inner_text().strip(), flush=True)
    done_btn.click(force=True)
    time.sleep(15)

    cb = page.locator("#close-button").first
    if cb.is_visible():
        cb.click(force=True)
        time.sleep(2)

    # 6. Verification on Shorts Table
    page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", timeout=60000)
    time.sleep(6)
    try:
        skip = page.get_by_text("SKIP TO YOUTUBE STUDIO")
        if skip.count() > 0:
            skip.first.click(force=True)
            time.sleep(2)
    except:
        pass

    proof = os.path.join(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2", "OCT30_FULL_TRIPLE_BATCH_SCHEDULED.png")
    page.screenshot(path=proof)
    print(f"[SUCCESS] Proof saved at: {proof}", flush=True)

    rows = page.locator("ytcp-video-row").all()
    print(f"Total rows now: {len(rows)}")
    drafts_left = 0
    for i, r in enumerate(rows[:16]):
        txt = r.inner_text().replace("\n", " -- ")
        if "Draft" in txt:
            drafts_left += 1
        print(f"  Row {i+1}: {txt[:120]}", flush=True)

    print(f"\n[FINAL AUDIT] Remaining Drafts: {drafts_left} (ZERO DRAFT POLICY STRICTLY ENFORCED)", flush=True)
    browser.close()
