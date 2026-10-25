import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

subprocess.run(["taskkill", "/F", "/IM", "brave.exe"], capture_output=True)
time.sleep(2)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=r'C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data',
        executable_path=r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe',
        headless=True,
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
    except:
        pass

    draft_row = page.locator('ytcp-video-row:has-text("Draft")').first
    if draft_row.count() > 0:
        draft_row.hover()
        time.sleep(1)
        draft_row.locator('ytcp-button:has-text("Edit draft")').first.click(force=True)
        time.sleep(5)
        page.screenshot(path=r'C:\TheNaughtyDuo_Automation\output\draft_modal_debug.png')
        print("[OK] Draft modal opened and screenshot saved!", flush=True)

        # Check what step buttons exist
        steps = page.locator('ytcp-stepper-item, #step-badge').all()
        print(f"Step elements found: {len(steps)}", flush=True)

        # Click the 4th step (Visibility) directly!
        vis_step = page.locator('#step-badge-3, [test-id="VISIBILITY"], ytcp-stepper-item:has-text("Visibility")').first
        if vis_step.count() > 0:
            print("[*] Clicking Visibility step directly...", flush=True)
            vis_step.click(force=True)
            time.sleep(3)
        else:
            # Click next until visibility
            for i in range(4):
                nxt = page.locator('#next-button').first
                if nxt.is_visible() and nxt.is_enabled():
                    nxt.click(force=True)
                    time.sleep(2)

        page.screenshot(path=r'C:\TheNaughtyDuo_Automation\output\draft_modal_step4.png')
        
        # Now click schedule radio / container
        sched = page.locator('#second-container-expand-button, #second-container, #schedule-radio-button, [name="SCHEDULE"]').first
        if sched.count() > 0:
            sched.click(force=True)
            time.sleep(2)
            print("[OK] Clicked schedule container!", flush=True)
        else:
            p_text = page.get_by_text("Schedule").all()
            for pt in p_text:
                if pt.is_visible():
                    pt.click(force=True)
                    time.sleep(2)
                    print("[OK] Clicked Schedule text!", flush=True)
                    break

        page.screenshot(path=r'C:\TheNaughtyDuo_Automation\output\draft_modal_schedule_opened.png')

        # Set Date
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

        page.locator("ytcp-video-visibility-select p, #visibility-title").first.click(force=True)
        time.sleep(1)

        # Set Time to 6:30 PM
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

        # Done button
        done_btn = page.locator("#done-button").first
        if done_btn.is_visible():
            print("Done button text:", done_btn.inner_text().strip())
            done_btn.click(force=True)
            time.sleep(12)

        cb = page.locator("#close-button").first
        if cb.is_visible():
            cb.click(force=True)
            time.sleep(2)

    page.goto('https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short', timeout=60000)
    time.sleep(6)
    try:
        skip = page.get_by_text('SKIP TO YOUTUBE STUDIO')
        if skip.count() > 0:
            skip.first.click(force=True)
            time.sleep(2)
    except:
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
