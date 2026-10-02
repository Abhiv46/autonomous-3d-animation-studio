import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Master Style Block
STYLE_BLOCK = (
    "Semi-realistic 3D animated style, Pixar/Disney-inspired rendering with soft painterly texture, "
    "warm cinematic color grading. Vibrant lighting, rich subsurface skin scattering, fluid cartoon character animation."
)
AVOID_BLOCK = "Avoid: flat 2D look, inconsistent facial features, extra fingers, distorted hands, blurry background, style shifting mid-scene, anatomy errors, redesigned character"

KAAVYA_SOLO_PROMPT = f"""{STYLE_BLOCK}

Cozy sunlit living room with warm morning light streaming across a soft knitted carpet. High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. Full 3D CGI animation.
Adorable chubby toddler Kaavya (3.5 years old, cute double hair buns with pink scrunchies, rosy blushed cheeks, sweet pink cotton pajamas, sparkling large brown Disney eyes) decides to wear Papa's gigantic brown leather sneakers!
Her tiny feet are completely buried inside the oversized giant shoes. She takes slow, clumsy, adorable wobbly steps forward, holding both tiny chubby arms out sideways like airplane wings to keep balance!
She wobbles playfully, glances up at the camera with a cute innocent wide-eyed smile, and bursts into sweet joyous toddler giggles as she successfully takes three big steps!
Ultra-detailed textures: soft cotton pajamas, detailed leather on big shoes, soft carpet fibers, glowing skin subsurface scattering, cinematic shallow depth of field.
STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays.

{AVOID_BLOCK}"""

def main():
    print("=" * 65)
    print("  CONTROLLING LIVE DESKTOP BROWSER (WATCH YOUR SCREEN!)")
    print("=" * 65)

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        contexts = browser.contexts
        if not contexts or not contexts[0].pages:
            print("[!] No open pages found on CDP.")
            return

        page = contexts[0].pages[0]
        print(f"[+] Connected to live window! Active URL: {page.url}")

        page.wait_for_timeout(3000)

        # 1. Back button if a card is open
        back_btn = page.locator("button:has-text('Done'), button[aria-label*='back' i]").first
        if back_btn.count() > 0 and back_btn.is_visible():
            print("[Step 1] Closing overlay / returning to canvas...")
            back_btn.click(force=True)
            page.wait_for_timeout(2000)

        # 2. Add ingredients menu
        print("[Step 2] Clicking 'Add ingredients to the prompt box' button (+)...")
        add_btn = page.locator("button[aria-label='Add ingredients to the prompt box']").first
        if add_btn.count() > 0:
            add_btn.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)
            add_btn.click(force=True)
            print("[+] Clicked '+' button! Waiting for ingredients dialog...")
            page.wait_for_timeout(2000)

            # Look for kaavya
            overlay = page.locator(".cdk-overlay-pane, [role='dialog']").first
            if overlay.count() > 0:
                kaavya_item = overlay.locator("text='kaavya'").first
                if kaavya_item.count() > 0:
                    print("[+] Selecting character: 'kaavya'...")
                    kaavya_item.click(force=True)
                    page.wait_for_timeout(1500)

                    add_to_prompt = overlay.locator("button:has-text('Add to prompt')").first
                    if add_to_prompt.count() > 0:
                        add_to_prompt.click(force=True)
                        print("[✓] Clicked 'Add to prompt'! Attached @kaavya!")
                        page.wait_for_timeout(2000)

        # 3. Enter prompt into prompt box
        print("[Step 3] Entering prompt into prompt box...")
        editor = page.locator(".ProseMirror").first
        if editor.count() > 0:
            editor.click()
            page.wait_for_timeout(800)
            # Select all and delete old text if any
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            page.wait_for_timeout(500)
            editor.fill(KAAVYA_SOLO_PROMPT)
            print("[✓] Prompt successfully pasted into editor!")
            page.wait_for_timeout(2500)

        # 4. Trigger generation
        print("[Step 4] Starting generation...")
        gen_btn = page.locator("button[aria-label='Start generation']").first
        if gen_btn.count() > 0 and gen_btn.is_enabled():
            gen_btn.click(force=True)
            print("[✓] Clicked 'Start generation' button!")
        else:
            page.keyboard.press("Control+Enter")
            print("[✓] Pressed Control+Enter to start generation!")

        page.wait_for_timeout(4000)

        # 5. Check for approve modal
        approve_btn = page.locator("button:has-text('Always approve'), button:has-text('Approve')").first
        if approve_btn.count() > 0 and approve_btn.is_visible():
            print("[+] Approving prompt generation...")
            approve_btn.click(force=True)
            page.wait_for_timeout(2000)

        print("\n[🎉 SUCCESS] Generation has officially started on your screen!")
        print("Leaving browser OPEN on your desktop so you can watch the entire generation process!")

if __name__ == "__main__":
    main()
