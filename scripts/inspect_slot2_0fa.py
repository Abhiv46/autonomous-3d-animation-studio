from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    page.goto("https://flow.google.com/u/2/project/0fa549b9-b73f-4dac-8061-365fd0498eb2", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(4000)

    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\slot2_proj_0fa.png")
    
    # Check text of elements
    txts = page.locator("flow-grid-tile-container, .character-tile-container, [role='gridcell']").all()
    for idx, t in enumerate(txts):
        print(f"Tile {idx}: {t.inner_text().strip()[:50]}")
