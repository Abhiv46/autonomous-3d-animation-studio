import time
from playwright.sync_api import sync_playwright

IMAGE_PROMPT_SCENE3 = (
    "Generate 3D animated scene image: "
    "Cute Pixar 3D animated cartoon style, vibrant warm lighting, 9:16 vertical orientation. "
    "In front of a bedroom mirror, adorable toddler Kaavya (pink pajamas, two cute high hair buns with pink ribbon bows) striking a dramatic funny model pose in the giant pink high heels, hands on her tiny waist, head tilted with pure cute sass! "
    "Next to her, 5-year-old brother Kaartik (messy brown cartoon hair, blue and white striped t-shirt) sitting on the soft carpet holding his stomach laughing hysterically with joy! "
    "Bright cheerful bedroom ambiance, soft morning sunshine, ultra-clean Pixar 3D cartoon render, no 2D lines, no blur, no text overlays."
)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    editor = page.locator(".ProseMirror").first
    print("Found editor:", editor.count())
    if editor.count() > 0:
        editor.click(force=True)
        page.wait_for_timeout(500)

        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        page.wait_for_timeout(300)

        print("Pasting Scene 3 3D Image Prompt...")
        editor.fill(IMAGE_PROMPT_SCENE3)
        page.wait_for_timeout(1500)

        send_btn = page.locator("button.generate-icon-button, button[aria-label='Start generation'], button:has-text('arrow_forward')").last
        print("Send button found:", send_btn.count(), "enabled:", send_btn.is_enabled())
        if send_btn.count() > 0 and send_btn.is_enabled():
            print("Clicking Send button...")
            send_btn.click(force=True)
        else:
            print("Pressing Control+Enter...")
            page.keyboard.press("Control+Enter")

        page.wait_for_timeout(4000)

        approve_btn = page.locator("button:has-text('Approve'), button:has-text('Always approve')").first
        if approve_btn.count() > 0 and approve_btn.is_visible():
            print("Approving...")
            approve_btn.click(force=True)
            page.wait_for_timeout(2000)

    print("Scene 3 image generation triggered!")
