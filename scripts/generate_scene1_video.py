import time
from playwright.sync_api import sync_playwright

VIDEO_PROMPT_SCENE1 = (
    "Animate into 8-second 3D video (9:16 vertical): "
    "Slow cinematic eye-level push-in. Kaavya takes two clumsy, adorable wobbly steps in the giant pink heels, clacking comically on the floor. "
    "Her knees wobble playfully as she giggles looking at the camera. Kaartik claps his hands laughing and points at her tiny feet. "
    "Warm sunlight beams through the bedroom window. Fluid cartoon physics, expressive joyful facial animation. No flat 2D look, no line art, no text."
)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Select Scene 1 image from overlay
    overlay = page.locator(".cdk-overlay-pane, [role='dialog'], [role='menu']").first
    scene1_item = overlay.locator("text='Toddler wearing giant high heels'").first
    print("Found Scene 1 item in menu:", scene1_item.count())
    if scene1_item.count() > 0:
        scene1_item.click(force=True)
        page.wait_for_timeout(1000)

        # Click Add to prompt
        add_btn = overlay.locator("button:has-text('Add to prompt')").first
        if add_btn.count() > 0:
            add_btn.click(force=True)
            print("Attached Scene 1 image to prompt box!")
            page.wait_for_timeout(1500)

    # Now attach Kaavya character
    plus_btn = page.locator("button.add-menu-trigger, button[aria-label='Add ingredients to the prompt box']").last
    if plus_btn.count() > 0:
        plus_btn.click(force=True)
        page.wait_for_timeout(1500)
        overlay = page.locator(".cdk-overlay-pane, [role='dialog'], [role='menu']").first
        kaavya_char = overlay.locator("text='Kaavya'").first
        if kaavya_char.count() > 0:
            kaavya_char.click(force=True)
            page.wait_for_timeout(1000)
            add_btn = overlay.locator("button:has-text('Add to prompt')").first
            if add_btn.count() > 0:
                add_btn.click(force=True)
                print("Attached Kaavya character to prompt box!")
                page.wait_for_timeout(1500)

    # Type Video Prompt
    editor = page.locator(".ProseMirror").first
    if editor.count() > 0:
        editor.click(force=True)
        page.wait_for_timeout(500)
        editor.fill(VIDEO_PROMPT_SCENE1)
        print("Pasted Scene 1 Video Prompt!")
        page.wait_for_timeout(1500)

        # Click Generate
        send_btn = page.locator("button.generate-icon-button, button[aria-label='Start generation'], button:has-text('arrow_forward')").last
        if send_btn.count() > 0 and send_btn.is_enabled():
            print("Clicking Start Generation for Scene 1 Video...")
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

    # Fast screenshot
    cdp = page.context.new_cdp_session(page)
    res = cdp.send("Page.captureScreenshot")
    import base64
    with open(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\scene1_video_started.png", "wb") as f:
        f.write(base64.b64decode(res["data"]))
    print("Scene 1 Video Generation successfully triggered!")
