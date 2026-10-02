import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Look for the element with text kaavya
    kaavya_item = page.locator("text='kaavya'").first
    print("Found kaavya item:", kaavya_item.count())
    if kaavya_item.count() > 0:
        print("Clicking kaavya item in modal...")
        kaavya_item.click(force=True)
        page.wait_for_timeout(2000)

        # Check if there is an 'Add' or 'Select' or 'Add to prompt' button
        add_btn = page.locator("button:has-text('Add to prompt'), button:has-text('Add'), button:has-text('Select')").first
        if add_btn.count() > 0 and add_btn.is_visible():
            print("Clicking Add button:", add_btn.inner_text())
            add_btn.click(force=True)
            page.wait_for_timeout(2000)

    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\after_kaavya_selection.png")
    print("Screenshot saved.")
