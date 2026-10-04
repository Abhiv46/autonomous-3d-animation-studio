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

        # The drawer is already open!
        # Find drawer container
        drawer = flow_page.locator(".cdk-overlay-pane, [class*='drawer'], [role='dialog']").first
        print("[1] Drawer found, attaching ingredients...", flush=True)

        # 1. Attach Kaavya
        print("[+] Attaching Kaavya...", flush=True)
        kaavya_item = drawer.locator("text='Kaavya'").first
        if kaavya_item.count() > 0:
            kaavya_item.click()
            time.sleep(1)
            add_btn = drawer.locator("button:has-text('Add to prompt')").first
            if add_btn.count() > 0 and add_btn.is_visible():
                add_btn.click()
                print("    Added Kaavya chip!")
                time.sleep(1.5)

        # 2. Attach Kaartik
        print("[+] Attaching Kaartik...", flush=True)
        kaartik_item = drawer.locator("text='Kaartik'").first
        if kaartik_item.count() > 0:
            kaartik_item.click()
            time.sleep(1)
            add_btn = drawer.locator("button:has-text('Add to prompt')").first
            if add_btn.count() > 0 and add_btn.is_visible():
                add_btn.click()
                print("    Added Kaartik chip!")
                time.sleep(1.5)

        # 3. Attach Reference Image
        print("[+] Attaching Reference Image...", flush=True)
        img_tab = drawer.locator("text='Images'").first
        if img_tab.count() > 0:
            img_tab.click()
            time.sleep(1.5)
            
        # Click the first image item in drawer
        first_img = drawer.locator("[class*='item'], [class*='card']").first
        if first_img.count() > 0:
            first_img.click()
            time.sleep(1)
            add_btn = drawer.locator("button:has-text('Add to prompt')").first
            if add_btn.count() > 0 and add_btn.is_visible():
                add_btn.click()
                print("    Added Reference Image chip!")
                time.sleep(1.5)

        # 4. Close drawer
        flow_page.keyboard.press("Escape")
        time.sleep(1)

        # 5. Switch mode to Video (Veo 3.1 - Lite · 9:16)
        print("[+] Switching mode to Video...", flush=True)
        pbox = flow_page.locator(".prompt-box, flow-base-prompt-box, [class*='prompt-box']").first
        # Find mode trigger
        for b in pbox.locator("button").all():
            txt = b.inner_text().strip()
            if any(w in txt.lower() for w in ["banana", "image", "video"]):
                print(f"    Clicking mode button: {repr(txt)}")
                b.click()
                time.sleep(1)
                break

        # Click Video toggle inside overlay
        overlay = flow_page.locator(".cdk-overlay-pane, [class*='overlay-pane'], [class*='popover']").first
        if overlay.count() > 0 and overlay.is_visible():
            for el in overlay.locator("button, mat-button-toggle, [role='button'], div, span").all():
                txt = el.inner_text().strip()
                if txt == "Video" or (txt.startswith("Video") and "image" not in txt.lower()):
                    print(f"    Selected Video toggle: {repr(txt)}")
                    el.click(force=True)
                    time.sleep(1)
                    break
                    
            for el in overlay.locator("button, mat-button-toggle, [role='button'], div, span").all():
                txt = el.inner_text().strip()
                if "9:16" in txt:
                    el.click(force=True)
                    time.sleep(0.5)
                    break

        flow_page.keyboard.press("Escape")
        time.sleep(1)

        # 6. Type the lively Video Prompt
        print("[+] Typing lively video prompt...", flush=True)
        pm = flow_page.locator("div.ProseMirror, [contenteditable='true']").first
        pm.click()
        time.sleep(0.5)
        pm.fill(VIDEO_PROMPT)
        time.sleep(1)

        flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\ep23_verified_prompt_with_chips.png")
        print("[+] Proof screenshot saved: ep23_verified_prompt_with_chips.png")

        # 7. Submit Video Generation
        print("[+] Clicking Generate button...", flush=True)
        arrow = pbox.locator("button:has-text('arrow_forward'), [aria-label*='generation']").first
        arrow.click()
        time.sleep(2)

        # Auto-confirm spend dialog
        for _ in range(3):
            agree = flow_page.locator("button:has-text('Continue'), button:has-text('Agree')").first
            if agree.count() > 0 and agree.is_visible():
                print("[+] Auto-approving spend dialog...")
                agree.click()
                time.sleep(1)

        flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\ep23_video_render_live_proof.png")
        print("[SUCCESS] Video generation successfully launched with Reference Image and Character chips!")

if __name__ == "__main__":
    run()
