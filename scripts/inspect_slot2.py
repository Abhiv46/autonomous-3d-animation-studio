from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    page.goto("https://flow.google.com/u/2/", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(4000)

    # Find project cards
    cards = page.locator("a[href*='/u/2/project/']").all()
    print("Found Slot 2 cards:", len(cards))
    for c in cards:
        href = c.get_attribute("href")
        txt = c.inner_text().strip()
        print(f"Project: {href} | Text: '{txt}'")

    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\slot2_dashboard.png")
