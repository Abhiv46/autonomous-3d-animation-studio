from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Click Done
    done_btn = page.locator("button:has-text('Done')").first
    if done_btn.count() > 0 and done_btn.is_visible():
        done_btn.click(force=True)
        page.wait_for_timeout(2000)

    # Capture fast screenshot
    cdp = page.context.new_cdp_session(page)
    res = cdp.send("Page.captureScreenshot")
    import base64
    with open(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\back_to_canvas.png", "wb") as f:
        f.write(base64.b64decode(res["data"]))
    print("Back to canvas saved!")
