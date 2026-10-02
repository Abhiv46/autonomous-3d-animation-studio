from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    start_btn = page.locator("button:has-text('Start')").first
    print("Clicking 'Start' button...")
    start_btn.click(force=True)
    page.wait_for_timeout(2000)

    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\after_start_btn_click.png")

    # Check visible items or overlays
    items = page.locator(".cdk-overlay-pane, [role='dialog'], [role='menu']").all()
    print("Overlays count:", len(items))
    for it in items:
        try:
            print("Overlay text:", it.inner_text()[:200])
        except Exception:
            pass
