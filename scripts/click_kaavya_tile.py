from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Look for the card or tile that contains 'kaavya'
    kaavya_tile = page.locator("text='kaavya'").first
    print("Clicking 'kaavya' tile on canvas...")
    kaavya_tile.click(force=True)
    page.wait_for_timeout(2000)

    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\after_kaavya_tile_click.png")

    # Check visible buttons now
    btns = page.locator("button").all()
    for b in btns:
        try:
            if b.is_visible():
                aria = b.get_attribute("aria-label") or ""
                txt = b.inner_text() or ""
                if any(k in (aria + txt).lower() for k in ["prompt", "use", "add", "ingredient", "start"]):
                    print(f"Match: aria='{aria}', text='{txt.strip()}'")
        except Exception:
            pass
