import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

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
    print("  OPENING 'THE NAUGHTY DUO' PROJECT & STARTING GENERATION")
    print("=" * 65)

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = browser.contexts[0].pages[0]

        # Step 1: Click on "The Naughty Duo" project card
        print("[Step 1] Clicking 'The Naughty Duo' project card on screen...")
        project_card = page.locator("text='The Naughty Duo'").first
        if project_card.count() > 0:
            project_card.click(force=True)
            print("[+] Clicked project card! Waiting 6s for canvas to load...")
            page.wait_for_timeout(6000)
        else:
            print("[*] Project card not found, navigating directly via URL...")
            page.goto("https://flow.google.com/u/0/project/1876f0f7-bc42-4764-86c9-35d76cb3a615")
            page.wait_for_timeout(6000)

        print("[+] Current URL:", page.url)

        # Step 2: Close any open card/viewer if present
        back_btn = page.locator("button:has-text('Done'), button[aria-label*='back' i]").first
        if back_btn.count() > 0 and back_btn.is_visible():
            print("[*] Returning to canvas view...")
            back_btn.click(force=True)
            page.wait_for_timeout(2000)

        # Step 3: Click Add ingredients (+)
        print("[Step 2] Clicking 'Add ingredients' (+) button...")
        add_btn = page.locator("button[aria-label='Add ingredients to the prompt box']").first
        if add_btn.count() > 0 and add_btn.is_visible():
            add_btn.click(force=True)
            page.wait_for_timeout(2000)

            overlay = page.locator(".cdk-overlay-pane, [role='dialog']").first
            if overlay.count() > 0:
                kaavya_item = overlay.locator("text='kaavya'").first
                if kaavya_item.count() > 0:
                    print("[+] Selecting 'kaavya' character asset...")
                    kaavya_item.click(force=True)
                    page.wait_for_timeout(1000)

                    add_to_prompt = overlay.locator("button:has-text('Add to prompt')").first
                    if add_to_prompt.count() > 0:
                        add_to_prompt.click(force=True)
                        print("[✓] Attached @kaavya to prompt box!")
                        page.wait_for_timeout(1500)

        # Step 4: Enter Prompt
        print("[Step 3] Entering prompt into prompt box...")
        editor = page.locator(".ProseMirror").first
        if editor.count() > 0:
            editor.click()
            page.wait_for_timeout(500)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            page.wait_for_timeout(300)
            editor.fill(KAAVYA_SOLO_PROMPT)
            print("[✓] Prompt entered into prompt box!")
            page.wait_for_timeout(2000)

        # Step 5: Start Generation
        print("[Step 4] Clicking 'Start generation'...")
        gen_btn = page.locator("button[aria-label='Start generation']").first
        if gen_btn.count() > 0 and gen_btn.is_enabled():
            gen_btn.click(force=True)
            print("[✓] Clicked 'Start generation' button!")
        else:
            page.keyboard.press("Control+Enter")
            print("[✓] Pressed Control+Enter to start generation!")

        page.wait_for_timeout(4000)

        # Approve dialog if any
        approve_btn = page.locator("button:has-text('Approve'), button:has-text('Always approve')").first
        if approve_btn.count() > 0 and approve_btn.is_visible():
            print("[+] Approving prompt...")
            approve_btn.click(force=True)
            page.wait_for_timeout(2000)

        print("\n[🎉 SUCCESS] Generation is now running live on your screen!")
        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\generation_started_live.png")

if __name__ == "__main__":
    main()
