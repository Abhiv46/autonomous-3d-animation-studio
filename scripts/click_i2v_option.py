import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Look for "Animate just the image (I2V)"
    i2v_opt = page.locator("text='Animate just the image (I2V)'").first
    print("Found I2V option:", i2v_opt.count())
    if i2v_opt.count() > 0:
        print("Clicking 'Animate just the image (I2V)'...")
        i2v_opt.click(force=True)
        page.wait_for_timeout(2000)

        # Check if there is a Confirm or Submit or Next button
        confirm_btn = page.locator("button:has-text('Confirm'), button:has-text('Proceed'), button:has-text('Submit'), button:has-text('Continue')").first
        if confirm_btn.count() > 0 and confirm_btn.is_visible():
            print("Clicking confirm button:", confirm_btn.inner_text())
            confirm_btn.click(force=True)
            page.wait_for_timeout(2000)

        # Check approval
        approve_btn = page.locator("button:has-text('Approve'), button:has-text('Always approve')").first
        if approve_btn.count() > 0 and approve_btn.is_visible():
            print("Approving...")
            approve_btn.click(force=True)
            page.wait_for_timeout(2000)

    # Capture fast screenshot
    cdp = page.context.new_cdp_session(page)
    res = cdp.send("Page.captureScreenshot")
    import base64
    with open(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\after_i2v_click.png", "wb") as f:
        f.write(base64.b64decode(res["data"]))
    print("Done clicking I2V!")
