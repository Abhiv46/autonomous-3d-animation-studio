from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    close_side = page.locator("button:has-text('close'), button[aria-label='Close panel'], button[aria-label*='close' i]").first
    print("Found close side button:", close_side.count())
    if close_side.count() > 0:
        close_side.click(force=True)
        page.wait_for_timeout(1500)

    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\full_canvas_916.png")
