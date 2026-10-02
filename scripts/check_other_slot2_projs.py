from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    for pid in ["abaca554-2cdc-4fc1-89fc-420b202d4c62", "0fa549b9-b73f-4dac-8061-365fd0498eb2", "9b878761-40e8-4c26-b458-6fc15d1210f8"]:
        page.goto(f"https://flow.google.com/u/2/project/{pid}", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        title = page.locator("h1, .project-name, header").first.inner_text().strip() if page.locator("h1, .project-name, header").count() > 0 else ""
        tiles = page.locator("flow-grid-tile-container, .character-tile-container, div[role='gridcell']").all()
        print(f"Project {pid[:8]}: Title='{title}', Tiles={len(tiles)}")
