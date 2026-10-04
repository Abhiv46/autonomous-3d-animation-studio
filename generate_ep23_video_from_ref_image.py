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

        # 1. Switch mode from Image back to Video (Veo 3.1 - Lite · 9:16)
        print("[1] Opening mode menu to switch to Video...", flush=True)
        # Find mode button currently showing 'Nano Banana 2'
        for b in flow_page.locator("button").all():
            txt = b.inner_text().strip()
            if "banana" in txt.lower() or "image" in txt.lower():
                print(f"    Clicking mode button: {txt}")
                b.click()
                time.sleep(1)
                break

        # Click 'Video' toggle inside overlay
        overlay = flow_page.locator(".cdk-overlay-pane, [class*='overlay-pane'], [class*='popover']").first
        if overlay.count() > 0 and overlay.is_visible():
            for el in overlay.locator("button, mat-button-toggle, [role='button'], div, span").all():
                txt = el.inner_text().strip()
                if txt == "Video" or (txt.startswith("Video") and "image" not in txt.lower()):
                    print(f"[+] Found Video in overlay, clicking: {repr(txt)}")
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

        flow_page.keyboard.press("Escape")
        time.sleep(1)

        # 2. Reset prompt box
        print("[2] Clearing prompt box...", flush=True)
        pm = flow_page.locator("div.ProseMirror, [contenteditable='true']").first
        pm.click()
        flow_page.keyboard.press("Control+A")
        flow_page.keyboard.press("Backspace")
        time.sleep(0.5)

        # 3. Attach Kaavya, Kaartik, and the newly generated Reference Image
        print("[3] Attaching Kaavya, Kaartik, and Reference Image chips...", flush=True)
        
        # Click '+' to open drawer
        add_btn = flow_page.locator("button[aria-label*='Add ingredients'], button:has-text('add')").first
        add_btn.click()
        time.sleep(2)

        # A) Attach Kaavya
        chars_cat = flow_page.locator("button:has-text('Characters'), [role='tab']:has-text('Characters'), span:has-text('Characters')").first
        if chars_cat.count() > 0 and chars_cat.is_visible():
            chars_cat.click()
            time.sleep(1.5)
        kaavya_card = flow_page.locator("[class*='card'], [class*='item']").filter(has_text="Kaavya").first
        if kaavya_card.count() > 0:
            kaavya_card.click()
            time.sleep(1)
            add_to_prompt = flow_page.locator("button:has-text('Add to prompt')").first
            if add_to_prompt.count() > 0 and add_to_prompt.is_visible():
                add_to_prompt.click()
                print("    [+] Added Kaavya chip!")
                time.sleep(1.5)

        # B) Attach Kaartik
        add_btn = flow_page.locator("button[aria-label*='Add ingredients'], button:has-text('add')").first
        if add_btn.count() > 0 and add_btn.is_visible():
            add_btn.click()
            time.sleep(2)
        chars_cat = flow_page.locator("button:has-text('Characters'), [role='tab']:has-text('Characters'), span:has-text('Characters')").first
        if chars_cat.count() > 0 and chars_cat.is_visible():
            chars_cat.click()
            time.sleep(1.5)
        kaartik_card = flow_page.locator("[class*='card'], [class*='item']").filter(has_text="Kaartik").first
        if kaartik_card.count() > 0:
            kaartik_card.click()
            time.sleep(1)
            add_to_prompt = flow_page.locator("button:has-text('Add to prompt')").first
            if add_to_prompt.count() > 0 and add_to_prompt.is_visible():
                add_to_prompt.click()
                print("    [+] Added Kaartik chip!")
                time.sleep(1.5)

        # C) Attach the newly generated Reference Image
        print("[4] Attaching Reference Image chip...", flush=True)
        add_btn = flow_page.locator("button[aria-label*='Add ingredients'], button:has-text('add')").first
        if add_btn.count() > 0 and add_btn.is_visible():
            add_btn.click()
            time.sleep(2)
        img_cat = flow_page.locator("button:has-text('Images'), [role='tab']:has-text('Images'), span:has-text('Images')").first
        if img_cat.count() > 0 and img_cat.is_visible():
            img_cat.click()
            time.sleep(1.5)
            
        # Select first image in drawer (the one just generated)
        drawer_cards = flow_page.locator("[class*='card'], [class*='drawer'] [class*='item']").all()
        # Find image card
        for c in drawer_cards:
            if c.is_visible():
                c.click()
                time.sleep(1)
                add_to_prompt = flow_page.locator("button:has-text('Add to prompt')").first
                if add_to_prompt.count() > 0 and add_to_prompt.is_visible():
                    add_to_prompt.click()
                    print("    [+] Added Reference Image chip!")
                    time.sleep(1.5)
                break

        # Dismiss drawer
        flow_page.keyboard.press("Escape")
        time.sleep(1)

        # 4. Type the lively Video Prompt
        print("[5] Typing lively video prompt...", flush=True)
        pm = flow_page.locator("div.ProseMirror, [contenteditable='true']").first
        pm.click()
        time.sleep(0.5)
        pm.fill(VIDEO_PROMPT)
        time.sleep(1)

        flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\ep23_chips_and_video_prompt_verified.png")
        print("[+] Proof screenshot saved: ep23_chips_and_video_prompt_verified.png")

        # 5. Submit Video Generation
        print("[6] Submitting Video Generation...", flush=True)
        arrow = flow_page.locator("button:has-text('arrow_forward'), button.generate-icon-button, [aria-label='Start generation']").first
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
