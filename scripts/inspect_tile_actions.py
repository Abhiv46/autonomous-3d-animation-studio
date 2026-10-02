from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    char_tile = page.locator(".character-tile-container").all()
    print("Found character tiles:", len(char_tile))
    for idx, ct in enumerate(char_tile):
        txt = ct.inner_text().strip()
        print(f"Tile {idx}: text='{txt}'")

    # Let's hover and click on kaavya tile (index that contains 'kaavya')
    for ct in char_tile:
        if "kaavya" in ct.inner_text().lower():
            print("Found kaavya tile! Hovering...")
            ct.hover()
            page.wait_for_timeout(1000)
            
            # Check buttons inside this tile
            tile_btns = ct.locator("button, [role='button']").all()
            print("Buttons inside kaavya tile:", len(tile_btns))
            for b in tile_btns:
                print("Tile button:", b.get_attribute("aria-label"), b.inner_text().strip())

            # Click it
            ct.click(force=True)
            page.wait_for_timeout(1500)
            break

    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\after_hover_kaavya_tile.png")
