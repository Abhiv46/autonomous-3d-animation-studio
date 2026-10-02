from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Find the image tiles on the canvas
    # Tile 3 from left is Scene 1
    tiles = page.locator("flow-grid-tile-container, [role='gridcell'], .flow-grid-tile").all()
    print("Found grid tiles:", len(tiles))

    # Let's inspect the first 4 tiles
    for idx in range(min(4, len(tiles))):
        t = tiles[idx]
        print(f"Tile {idx}: text='{t.inner_text().strip()[:60]}'")
        t_btns = t.locator("button").all()
        for b in t_btns:
            print(f"   Tile {idx} button: aria='{b.get_attribute('aria-label')}', text='{b.inner_text().strip()}'")
