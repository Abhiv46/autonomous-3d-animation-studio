import time
from playwright.sync_api import sync_playwright

IMAGE_PROMPT_SCENE2 = (
    "Generate 3D animated scene image: "
    "Cute Pixar 3D animated cartoon style, vibrant warm lighting, 9:16 vertical orientation. "
    "Kaartik (messy brown cartoon hair, blue and white striped t-shirt, denim shorts) standing with hands on his hips comically pretending to be strict Mummy, pointing a finger with an exaggerated funny scowl! "
    "Kaavya (pink pajamas, two cute high hair buns with pink ribbon bows) frozen mid-step in the giant pink high heels, looking up with innocent wide puppy-dog cartoon eyes and biting her lower lip playfully. "
    "Cozy bedroom doorway background with soft golden morning sunlight. Clean 3D cartoon look, soft textures, no 2D lines, no text overlays."
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

        print("Pasting Scene 2 3D Image Prompt...")
        editor.fill(IMAGE_PROMPT_SCENE2)
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

        # Check approval
        approve_btn = page.locator("button:has-text('Approve'), button:has-text('Always approve')").first
        if approve_btn.count() > 0 and approve_btn.is_visible():
            print("Approving...")
            approve_btn.click(force=True)
            page.wait_for_timeout(2000)

    print("Scene 2 image generation triggered!")
