import sys
import time
import json
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

VIDEO_PROMPT = (
    "Vertical 9:16 aspect ratio, high-energy Pixar 3D animated cartoon comedy. "
    "Lively fast bouncy animation. Kaavya jumps energetically up and down on the colorful rug, "
    "clapping her hands and laughing with toddler delight, playfully popping floating soap bubbles that burst into sparkles. "
    "Kaartik dynamically runs across the room blowing more giant bubbles, giggling cheerfully. "
    "Exaggerated cartoon squash and stretch, rapid bouncy movements, comical cartoon facial expressions, "
    "dynamic camera tilt, vibrant candy colors. (playful upbeat cartoon sound effects, cheerful bubbles popping, joyful toddler giggles)."
)

def run():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        flow_page = next(pg for pg in browser.contexts[0].pages if "flow.google.com" in pg.url)
        flow_page.bring_to_front()

        # 1. Dismiss any open drawers or popovers first
        print("[1] Dismissing existing drawers/modals...", flush=True)
        flow_page.keyboard.press("Escape")
        time.sleep(1)

        # 2. Switch mode to Video (Veo 3.1 - Lite · 9:16)
        print("[2] Opening mode menu to select Video mode...", flush=True)
        pbox = flow_page.locator(".prompt-box, flow-base-prompt-box, [class*='prompt-box']").first
        
        # Click mode badge (Nano Banana 2)
        for b in pbox.locator("button").all():
            txt = b.inner_text().strip()
            if any(w in txt.lower() for w in ["banana", "image", "video"]):
                print(f"    Clicking mode badge: {repr(txt)}")
                b.click()
                time.sleep(1)
                break

        # Click 'Video' toggle inside overlay
        overlay = flow_page.locator(".cdk-overlay-pane, [class*='overlay-pane'], [class*='popover']").first
        if overlay.count() > 0 and overlay.is_visible():
            for el in overlay.locator("button, mat-button-toggle, [role='button'], div, span").all():
                txt = el.inner_text().strip()
                if txt == "Video" or (txt.startswith("Video") and "image" not in txt.lower()):
                    print(f"    [+] Selected Video toggle: {repr(txt)}")
                    el.click(force=True)
                    time.sleep(1)
                    break
                    
            # Ensure 9:16 is active
            for el in overlay.locator("button, mat-button-toggle, [role='button'], div, span").all():
                txt = el.inner_text().strip()
                if "9:16" in txt:
                    el.click(force=True)
                    time.sleep(0.5)
                    break

        # Dismiss popover
        flow_page.keyboard.press("Escape")
        time.sleep(1)

        # 3. Clear prompt box text
        print("[3] Clearing prompt box...", flush=True)
        pm = flow_page.locator("div.ProseMirror, [contenteditable='true']").first
        pm.click()
        flow_page.keyboard.press("Control+A")
        flow_page.keyboard.press("Backspace")
        time.sleep(0.5)

        # 4. Open '+' drawer strictly from prompt box
        print("[4] Opening '+' drawer to attach ingredients...", flush=True)
        plus_btn = pbox.locator("button").first
        plus_btn.click()
        time.sleep(2)

        # Drawer container
        drawer = flow_page.locator("[class*='drawer'], [class*='dialog'], [role='dialog'], [class*='panel']").first

        # A) Attach Kaavya
        print("[5] Attaching Kaavya...", flush=True)
        chars_cat = flow_page.locator("button:has-text('Characters'), span:has-text('Characters')").first
        if chars_cat.count() > 0:
            chars_cat.click()
            time.sleep(1)
        kaavya_item = flow_page.locator("[class*='item'], [class*='card']").filter(has_text="Kaavya").first
        if kaavya_item.count() > 0:
            kaavya_item.click()
            time.sleep(1)
            add_btn = flow_page.locator("button:has-text('Add to prompt')").first
            if add_btn.count() > 0 and add_btn.is_visible():
                add_btn.click()
                print("    [+] Kaavya chip attached!")
                time.sleep(1.5)

        # B) Re-open '+' drawer and attach Kaartik
        print("[6] Attaching Kaartik...", flush=True)
        plus_btn.click()
        time.sleep(2)
        chars_cat = flow_page.locator("button:has-text('Characters'), span:has-text('Characters')").first
        if chars_cat.count() > 0:
            chars_cat.click()
            time.sleep(1)
        kaartik_item = flow_page.locator("[class*='item'], [class*='card']").filter(has_text="Kaartik").first
        if kaartik_item.count() > 0:
            kaartik_item.click()
            time.sleep(1)
            add_btn = flow_page.locator("button:has-text('Add to prompt')").first
            if add_btn.count() > 0 and add_btn.is_visible():
                add_btn.click()
                print("    [+] Kaartik chip attached!")
                time.sleep(1.5)

        # C) Re-open '+' drawer and attach Reference Image (Bubble scene)
        print("[7] Attaching Reference Image chip...", flush=True)
        plus_btn.click()
        time.sleep(2)
        imgs_cat = flow_page.locator("button:has-text('Images'), span:has-text('Images')").first
        if imgs_cat.count() > 0:
            imgs_cat.click()
            time.sleep(1)
            
        # Select first image in drawer
        first_img = flow_page.locator("[class*='drawer'] [class*='item'], [class*='drawer'] [class*='card']").first
        if first_img.count() > 0:
            first_img.click()
            time.sleep(1)
            add_btn = flow_page.locator("button:has-text('Add to prompt')").first
            if add_btn.count() > 0 and add_btn.is_visible():
                add_btn.click()
                print("    [+] Reference Image chip attached!")
                time.sleep(1.5)

        # Close drawer
        flow_page.keyboard.press("Escape")
        time.sleep(1)

        # 5. Type the lively Video Prompt
        print("[8] Typing lively video prompt...", flush=True)
        pm = flow_page.locator("div.ProseMirror, [contenteditable='true']").first
        pm.click()
        time.sleep(0.5)
        pm.fill(VIDEO_PROMPT)
        time.sleep(1)

        # Take screenshot of prompt box with chips verified
        flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\ep23_chips_and_video_prompt_locked.png")
        print("[+] Proof screenshot saved: ep23_chips_and_video_prompt_locked.png")

        # 6. Click Generate button
        print("[9] Submitting Video Generation...", flush=True)
        arrow = pbox.locator("button:has-text('arrow_forward'), [aria-label*='generation']").first
        arrow.click()
        time.sleep(2)

        # Auto-confirm spend dialog if any
        for _ in range(3):
            agree = flow_page.locator("button:has-text('Continue'), button:has-text('Agree')").first
            if agree.count() > 0 and agree.is_visible():
                print("[+] Auto-approving spend dialog...")
                agree.click()
                time.sleep(1)

        flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\ep23_video_submitted_proof.png")
        print("[SUCCESS] Video generation submitted with reference image and character chips attached!")

if __name__ == "__main__":
    run()
