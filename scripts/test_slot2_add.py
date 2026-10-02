from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    add_btn = page.locator("button[aria-label='Add ingredients to the prompt box']").first
    print("Found add button:", add_btn.count())
    if add_btn.count() > 0:
        add_btn.click(force=True)
        page.wait_for_timeout(2000)

    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\slot2_add_menu.png")
    
    # Check overlays
    items = page.locator(".cdk-overlay-pane, [role='dialog'], [role='menu']").all()
    for it in items:
        try:
            print("Overlay text:", it.inner_text()[:250])
        except Exception:
            pass
