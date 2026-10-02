from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    img_dropdown = page.locator("button:has-text('Images'), div:has-text('Images')").first
    print("Clicking Images dropdown...")
    img_dropdown.click(force=True)
    page.wait_for_timeout(1500)

    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\images_dropdown_options.png")

    opts = page.locator("[role='menuitem'], [role='option'], .cdk-overlay-pane li, .cdk-overlay-pane button").all()
    for o in opts:
        try:
            print("Dropdown Option:", o.inner_text().strip())
        except Exception:
            pass
