from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Open first project in slot 2
    page.goto("https://flow.google.com/u/2/project/1fc877d7-73dd-4627-b635-df6b3549ee9e", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    print("Project 1 URL:", page.url)
    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\slot2_proj1.png")
