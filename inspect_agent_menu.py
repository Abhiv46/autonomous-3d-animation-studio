from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    flow_page = next(pg for pg in browser.contexts[0].pages if "flow.google.com" in pg.url)
    
    # Find the 'Agent' button / chip
    btns = flow_page.locator("button").all()
    for b in btns:
        if b.inner_text().strip() == "Agent":
            print("Found Agent button, clicking...")
            b.click()
            break
            
    flow_page.wait_for_timeout(1000)
    flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\agent_dropdown_menu.png")
    
    # Print menu options
    opts = flow_page.locator("[role='menuitem'], [role='option'], button, div").all()
    found = set()
    for o in opts:
        try:
            t = o.inner_text().strip()
            if t in ["Image", "Video", "Agent", "Nano Banana 2", "Veo 3.1 - Lite", "Veo 2", "Tools"]:
                found.add(t)
        except Exception:
            pass
    print("Found options:", found)
