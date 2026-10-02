from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Look for approval button
    appr = page.locator("button:has-text('Approve'), button:has-text('Always approve')").all()
    print("Approve buttons found:", len(appr))
    for a in appr:
        if a.is_visible():
            print("Clicking approve button on screen...")
            a.click(force=True)
            page.wait_for_timeout(2000)

    # Check for newly generated images/cards
    images = page.locator("img[alt*='generation' i], img[src*='flow-content']").all()
    print("Generated images found:", len(images))

    # Check text inside right panel
    panel = page.locator(".chat-container, aside, .right-panel").first
    if panel.count() > 0:
        print("Panel text preview:")
        print(panel.inner_text()[-400:])

    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\chat_after_submit.png", timeout=15000)
    print("Screenshot saved!")
