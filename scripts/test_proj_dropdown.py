from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Project dropdown at top left
    tnd_btn = page.locator("button:has-text('The Naughty Duo'), [aria-label*='project' i]").first
    print("Clicking project dropdown...")
    tnd_btn.click(force=True)
    page.wait_for_timeout(1500)

    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\project_dropdown_options.png")

    opts = page.locator("[role='menuitem'], [role='option'], .cdk-overlay-pane div").all()
    for o in opts[:15]:
        try:
            txt = o.inner_text().strip()
            if txt:
                print("Project Option:", txt)
        except Exception:
            pass
