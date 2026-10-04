from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    flow_page = next(pg for pg in browser.contexts[0].pages if "flow.google.com" in pg.url)
    
    # Click the mode trigger button
    btns = flow_page.locator("button").all()
    for b in btns:
        txt = b.inner_text().strip()
        if "video" in txt.lower() or "720p" in txt.lower():
            print(f"Clicking mode button: {txt}")
            b.click()
            break
            
    flow_page.wait_for_timeout(1000)
    flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\mode_options_opened.png")
    
    # Check all options visible
    opts = flow_page.locator("[role='tab'], [role='menuitem'], [role='option'], button, div").all()
    for o in opts:
        try:
            t = o.inner_text().strip()
            if t in ["Image", "Video", "Banana", "Veo", "9:16", "16:9"]:
                print("Visible option:", t)
        except Exception:
            pass
