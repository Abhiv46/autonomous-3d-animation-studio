from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    flow_page = next(pg for pg in browser.contexts[0].pages if "flow.google.com" in pg.url)
    
    # Click close button on right panel
    # We saw the 'x' button at top right of panel
    btns = flow_page.locator("button").all()
    for b in btns:
        txt = b.inner_text().strip()
        label = b.get_attribute("aria-label") or ""
        if txt in ["close", "X", "x"] or "close" in label.lower():
            print(f"Clicking button: txt='{txt}', label='{label}'")
            b.click()
            break
            
    flow_page.wait_for_timeout(2000)
    flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\after_panel_closed.png")
    print("Screenshot saved!")
