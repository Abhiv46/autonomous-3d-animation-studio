from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    for slot in [1, 2, 3]:
        page.goto(f"https://flow.google.com/u/{slot}/", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
        cards = page.locator("a[href*='/project/']").all()
        print(f"Slot {slot} has {len(cards)} projects: URL={page.url}")
        for c in cards:
            print("   Proj:", c.get_attribute("href"), c.inner_text().strip()[:40])
