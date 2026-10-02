from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    model_btn = page.locator("button:has-text('Nano Banana 2'), [aria-label*='model' i]").first
    print("Clicking model selector button...")
    model_btn.click(force=True)
    page.wait_for_timeout(1500)

    # Check menu options
    opts = page.locator(".cdk-overlay-pane button, [role='menuitem'], [role='option'], .cdk-overlay-pane li").all()
    print("Found model options:", len(opts))
    for o in opts:
        try:
            print("   Model Option:", o.inner_text().strip())
        except Exception:
            pass
