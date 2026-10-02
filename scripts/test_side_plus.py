from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Click + button in the side chat panel
    plus_btn = page.locator("button.add-menu-trigger, button[aria-label='Add ingredients to the prompt box']").last
    print("Found plus button:", plus_btn.count())
    if plus_btn.count() > 0:
        plus_btn.click(force=True)
        page.wait_for_timeout(1500)

    # Capture CDP screenshot
    cdp = page.context.new_cdp_session(page)
    res = cdp.send("Page.captureScreenshot")
    import base64
    with open(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\side_plus_menu.png", "wb") as f:
        f.write(base64.b64decode(res["data"]))
    print("Plus menu screenshot saved!")

    # Check menu items
    items = page.locator(".cdk-overlay-pane button, [role='menuitem'], [role='option'], .cdk-overlay-pane li").all()
    print("Overlay items count:", len(items))
    for it in items[:15]:
        try:
            print("   Item:", it.inner_text().strip())
        except Exception:
            pass
