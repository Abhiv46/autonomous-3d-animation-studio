import time
from playwright.sync_api import sync_playwright

PROMPT_TEXT = (
    "Semi-realistic 3D animated style, Pixar/Disney-inspired rendering with soft painterly texture, warm cinematic color grading. "
    "Cozy sunlit living room with warm morning light streaming across a soft knitted carpet. High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. "
    "Adorable toddler Kaavya wearing Papa's gigantic oversized brown leather shoes, taking clumsy cute wobbly steps forward, balancing with arms spread out like airplane wings, smiling with joyful giggles! "
    "Ultra-detailed textures: soft cotton pajamas, detailed leather on big shoes, soft carpet fibers, glowing skin subsurface scattering. "
    "STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text overlays."
)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Find editor inside the prompt container
    editor = page.locator(".ProseMirror, textarea, [contenteditable='true']").first
    print("Found editor:", editor.count())
    if editor.count() > 0:
        editor.click(force=True)
        page.wait_for_timeout(500)

        print("Typing prompt into prompt box beside Kaavya character...")
        page.keyboard.type(PROMPT_TEXT, delay=5)
        page.wait_for_timeout(2000)

        # Click Start generation arrow button
        arrow_btn = page.locator("button.start-generation-button, button[aria-label='Start generation'], button:has-text('arrow_forward')").first
        if arrow_btn.count() == 0:
            arrow_btn = page.locator("button:has(mat-icon:has-text('arrow_forward'))").first

        print("Arrow button count:", arrow_btn.count())
        if arrow_btn.count() > 0 and arrow_btn.is_enabled():
            print("Clicking Start Generation button...")
            arrow_btn.click(force=True)
        else:
            print("Pressing Control+Enter...")
            page.keyboard.press("Control+Enter")

        page.wait_for_timeout(4000)

        # Check for approval dialog if any
        approve_btn = page.locator("button:has-text('Approve'), button:has-text('Always approve')").first
        if approve_btn.count() > 0 and approve_btn.is_visible():
            print("Approving dialog...")
            approve_btn.click(force=True)
            page.wait_for_timeout(2000)

    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\slot2_generation_live.png")
    print("Generation officially started!")
