from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    link = page.locator("a[href*='1876f0f7-bc42-4764-86c9-35d76cb3a615']").first
    print("Found project link:", link.count())
    if link.count() > 0:
        link.click(force=True)
    else:
        page.goto("https://flow.google.com/u/0/project/1876f0f7-bc42-4764-86c9-35d76cb3a615")

    page.wait_for_timeout(6000)
    print("New URL:", page.url)
    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\project_canvas_opened.png")
