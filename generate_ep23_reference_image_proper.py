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

IMAGE_PROMPT = (
    "Vertical 9:16 aspect ratio, ultra-colorful 3D Pixar animated cartoon comedy style. "
    "Living room floor with bright sunny pastel morning light. Exactly ONE toddler Kaavya (3.5 years old, "
    "bright pastel pink frock, twin high pigtail buns with pink ribbons, huge glossy brown cartoon eyes, "
    "blushing chubby rosy cheeks) jumping high in the air with joyful toddler laughter, mouth wide open, "
    "tiny chubby hands reaching up to pop colorful floating soap bubbles. Beside her, Exactly ONE 5-year-old Kaartik "
    "(yellow cartoon tee, denim shorts, smiling cartoon face) dynamically waving a bubble wand with lots of "
    "iridescent shiny bubbles filling the room. Expressive cute cartoon faces, high saturation, dynamic bouncy cartoon energy, "
    "Cocomelon Disney Pixar 3D aesthetic, zero photorealism, ultra-vibrant candy colors."
)

def main():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        flow_page = next(pg for pg in browser.contexts[0].pages if "flow.google.com" in pg.url)
        flow_page.bring_to_front()

        # 1. Clear any text in prompt box
        print("[1] Clearing prompt box...", flush=True)
        pm = flow_page.locator("div.ProseMirror, [contenteditable='true']").first
        pm.click()
        flow_page.keyboard.press("Control+A")
        flow_page.keyboard.press("Backspace")
        time.sleep(0.5)

        # 2. Attach Character Chips (Kaavya and Kaartik)
        print("[2] Opening '+' drawer to attach Kaavya and Kaartik...", flush=True)
        add_btn = flow_page.locator("button[aria-label*='Add ingredients'], button:has-text('add')").first
        add_btn.click()
        time.sleep(2)

        # Click Characters category in drawer sidebar
        chars_cat = flow_page.locator("button:has-text('Characters'), [role='tab']:has-text('Characters'), span:has-text('Characters')").first
        if chars_cat.count() > 0 and chars_cat.is_visible():
            chars_cat.click()
            time.sleep(1.5)

        # Find and click Kaavya
        print("[3] Attaching Kaavya...", flush=True)
        kaavya_card = flow_page.locator("[class*='card'], [class*='item']").filter(has_text="Kaavya").first
        if kaavya_card.count() > 0:
            kaavya_card.click()
            time.sleep(1)
            # Click white "Add to prompt" button
            add_to_prompt = flow_page.locator("button:has-text('Add to prompt')").first
            if add_to_prompt.count() > 0 and add_to_prompt.is_visible():
                add_to_prompt.click()
                print("    [+] Clicked 'Add to prompt' for Kaavya!")
                time.sleep(1.5)

        # Re-open '+' drawer if closed
        prompt_chips = flow_page.locator(".chip-image, .chip-container, mat-chip").count()
        print(f"    Chips in prompt box currently: {prompt_chips}")

        add_btn = flow_page.locator("button[aria-label*='Add ingredients'], button:has-text('add')").first
        if add_btn.count() > 0 and add_btn.is_visible():
            add_btn.click()
            time.sleep(2)

        # Find and click Kaartik
        print("[4] Attaching Kaartik...", flush=True)
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
                print("    [+] Clicked 'Add to prompt' for Kaartik!")
                time.sleep(1.5)

        # Close drawer if open
        flow_page.keyboard.press("Escape")
        time.sleep(1)

        # 3. Type the pure 3D Pixar Image Prompt
        print("[5] Typing Image Prompt into prompt box...", flush=True)
        pm = flow_page.locator("div.ProseMirror, [contenteditable='true']").first
        pm.click()
        time.sleep(0.5)
        pm.fill(IMAGE_PROMPT)
        time.sleep(1)

        flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\ep23_image_ready_to_generate.png")

        # 4. Click Generate button
        print("[6] Submitting Image Generation...", flush=True)
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

        print("[SUCCESS] Reference Image submitted! Waiting 30s for render...")
        time.sleep(30)

        flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\ep23_image_render_proof.png")
        print("[+] Finished render check screenshot saved to ep23_image_render_proof.png")

if __name__ == "__main__":
    main()
