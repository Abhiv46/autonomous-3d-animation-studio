from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Close modal
    close_btn = page.locator("button[aria-label='Close'], button:has-text('close')").first
    if close_btn.count() > 0:
        close_btn.click(force=True)
        page.wait_for_timeout(1000)

    # Now let's inspect the kaavya card element on the canvas
    kaavya_card = page.locator("text='kaavya'").first
    print("Found kaavya:", kaavya_card.count())
    
    # Let's inspect its parent container
    parent = kaavya_card.locator("..")
    print("Parent tag:", parent.evaluate("el => el.tagName"))
    print("Parent HTML:", parent.evaluate("el => el.outerHTML")[:250])

    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\canvas_kaavya_inspect.png")
