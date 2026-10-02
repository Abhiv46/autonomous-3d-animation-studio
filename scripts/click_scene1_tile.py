from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    tiles = page.locator("flow-grid-tile-container, [role='gridcell'], .flow-grid-tile").all()
    # Click Tile 2 (Scene 1)
    print("Clicking Tile 2 (Scene 1 Image)...")
    tiles[2].click(force=True)
    page.wait_for_timeout(2500)

    # Check visible buttons
    btns = page.locator("button").all()
    print("Viewer buttons:")
    for b in btns:
        try:
            if b.is_visible():
                txt = b.inner_text().strip()
                aria = b.get_attribute("aria-label") or ""
                if any(w in (txt + aria).lower() for w in ["video", "animate", "prompt", "use", "create", "start", "ingredient"]):
                    print(f"   Option: aria='{aria}', text='{txt}'")
        except Exception:
            pass

    # Capture CDP screenshot
    cdp = page.context.new_cdp_session(page)
    res = cdp.send("Page.captureScreenshot")
    import base64
    with open(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\scene1_viewer_open.png", "wb") as f:
        f.write(base64.b64decode(res["data"]))
    print("Viewer screenshot saved!")
