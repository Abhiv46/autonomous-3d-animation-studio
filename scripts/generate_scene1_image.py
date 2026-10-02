import time
from playwright.sync_api import sync_playwright

IMAGE_PROMPT_SCENE1 = (
    "Generate 3D animated scene image: "
    "Cute Pixar 3D animated cartoon style, vibrant warm lighting, 9:16 vertical orientation. "
    "Cozy sunlit bedroom doorway with a wooden shoe rack on the left. "
    "Adorable 3-year-old toddler Kaavya (chubby rosy cheeks, big sparkling brown cartoon eyes, two cute high hair buns with pink ribbon bows, soft light pink cotton pajamas) wearing adult-sized giant glossy pink high-heel shoes! "
    "Her tiny feet are slipping inside the oversized heels. She wobbles adorably on the cream carpet, holding both arms out like airplane wings to balance, laughing with a big open-mouthed joyous giggle. "
    "Next to her, 5-year-old brother Kaartik (messy brown cartoon hair, blue and white striped t-shirt, denim shorts) watches with a mischievous cheeky grin. "
    "Clean 3D animation, soft cartoon render, high quality, no 2D lines, no blur, no text overlays."
)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Target .ProseMirror directly
    editor = page.locator(".ProseMirror").first
    print("Found editor:", editor.count())
    if editor.count() > 0:
        editor.click()
        page.wait_for_timeout(500)

        # Clear existing text
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        page.wait_for_timeout(300)

        print("Pasting Scene 1 3D Image Prompt into prompt box on screen...")
        editor.fill(IMAGE_PROMPT_SCENE1)
        page.wait_for_timeout(1500)

        # Send button
        send_btn = page.locator("button.generate-icon-button, button[aria-label='Start generation'], button:has-text('arrow_forward')").first
        print("Send button found:", send_btn.count(), "enabled:", send_btn.is_enabled())
        if send_btn.count() > 0 and send_btn.is_enabled():
            print("Clicking Send button on screen...")
            send_btn.click(force=True)
        else:
            print("Pressing Control+Enter...")
            page.keyboard.press("Control+Enter")

        page.wait_for_timeout(4000)

        # Check for approval dialog
        approve_btn = page.locator("button:has-text('Approve'), button:has-text('Always approve')").first
        if approve_btn.count() > 0 and approve_btn.is_visible():
            print("Approving generation dialog...")
            approve_btn.click(force=True)
            page.wait_for_timeout(2000)

    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\scene1_image_generating.png")
    print("Scene 1 image generation triggered live on screen!")
