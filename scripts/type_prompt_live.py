import time
from playwright.sync_api import sync_playwright

STYLE_BLOCK = (
    "Semi-realistic 3D animated style, Pixar/Disney-inspired rendering with soft painterly texture, "
    "warm cinematic color grading. Vibrant lighting, rich subsurface skin scattering, fluid cartoon character animation."
)
AVOID_BLOCK = "Avoid: flat 2D look, inconsistent facial features, extra fingers, distorted hands, blurry background, style shifting mid-scene, anatomy errors, redesigned character"

KAAVYA_SOLO_PROMPT = (
    "Semi-realistic 3D animated style, Pixar/Disney-inspired rendering with soft painterly texture, warm cinematic color grading. "
    "Cozy sunlit living room with warm morning light streaming across a soft knitted carpet. High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. "
    "Adorable chubby toddler Kaavya (3.5 years old, cute double hair buns with pink scrunchies, rosy blushed cheeks, sweet pink cotton pajamas, sparkling large brown Disney eyes) decides to wear Papa's gigantic brown leather sneakers! "
    "Her tiny feet are completely buried inside the oversized giant shoes. She takes slow, clumsy, adorable wobbly steps forward, holding both tiny chubby arms out sideways like airplane wings to keep balance! "
    "She wobbles playfully, glances up at the camera with a cute innocent wide-eyed smile, and bursts into sweet joyous toddler giggles as she successfully takes three big steps! "
    "Ultra-detailed textures: soft cotton pajamas, detailed leather on big shoes, soft carpet fibers, glowing skin subsurface scattering. "
    "STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays."
)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Dismiss any open modal by pressing Escape
    page.keyboard.press("Escape")
    page.wait_for_timeout(1000)

    # Locate editor
    editor = page.locator(".ProseMirror, [contenteditable='true']").first
    print("Found editor:", editor.count())
    if editor.count() > 0:
        editor.click()
        page.wait_for_timeout(500)
        
        # Select all and delete
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        page.wait_for_timeout(500)

        # Type @kaavya first
        print("Typing @kaavya...")
        page.keyboard.type("@kaavya", delay=50)
        page.wait_for_timeout(1500)

        # If a dropdown menu appeared for mention, press Enter to select it
        menu_item = page.locator(".cdk-overlay-pane, [role='listbox'], [role='option'], .mention-suggestion").first
        if menu_item.count() > 0 and menu_item.is_visible():
            print("Mention dropdown visible, pressing Enter...")
            page.keyboard.press("Enter")
            page.wait_for_timeout(500)

        page.keyboard.press("Space")
        page.wait_for_timeout(300)

        # Now fill the full prompt
        print("Entering full prompt...")
        page.keyboard.type(KAAVYA_SOLO_PROMPT, delay=5)
        page.wait_for_timeout(1500)

        # Click Start Generation
        gen_btn = page.locator("button[aria-label='Start generation'], button:has-text('arrow_forward')").first
        print("Start generation button found:", gen_btn.count())
        if gen_btn.count() > 0 and gen_btn.is_enabled():
            print("Clicking Start generation button...")
            gen_btn.click(force=True)
        else:
            print("Pressing Control+Enter...")
            page.keyboard.press("Control+Enter")

        page.wait_for_timeout(4000)

        # Check for approval dialog
        approve_btn = page.locator("button:has-text('Approve'), button:has-text('Always approve')").first
        if approve_btn.count() > 0 and approve_btn.is_visible():
            print("Approving prompt...")
            approve_btn.click(force=True)
            page.wait_for_timeout(2000)

    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\live_generation_triggered.png")
    print("[✓] Finished trigger attempt.")
