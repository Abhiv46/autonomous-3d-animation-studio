import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Find Kaavya in overlay
    overlay = page.locator(".cdk-overlay-pane, [role='dialog']").first
    kaavya_opt = overlay.locator("text='Kaavya'").first
    print("Found Kaavya in overlay:", kaavya_opt.count())
    if kaavya_opt.count() > 0:
        print("Clicking Kaavya character...")
        kaavya_opt.click(force=True)
        page.wait_for_timeout(1000)

        # Check if there is an Add to prompt button
        add_btn = overlay.locator("button:has-text('Add to prompt'), button:has-text('Add')").first
        if add_btn.count() > 0 and add_btn.is_visible():
            print("Clicking Add to prompt button...")
            add_btn.click(force=True)
            page.wait_for_timeout(1500)

    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\slot2_kaavya_attached.png")
