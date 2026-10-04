from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    flow_page = next(pg for pg in browser.contexts[0].pages if "flow.google.com" in pg.url)
    flow_page.bring_to_front()
    
    # Locate the second card in the top row (Tile 2: Kaavya jumping)
    cards = flow_page.locator("flow-card, [class*='card']").all()
    print("Total cards:", len(cards))
    if len(cards) >= 2:
        print("Clicking Tile 2...")
        cards[1].click()
        time.sleep(2)
        
    flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\tile2_card_opened.png")
    
    # Check all buttons visible on the page/editor
    btns = flow_page.locator("button").all()
    print("Buttons visible after opening card:")
    for b in btns:
        try:
            txt = b.inner_text().strip()
            label = b.get_attribute("aria-label") or ""
            if any(w in (txt + label).lower() for w in ["animate", "video", "create", "prompt", "edit", "add", "more"]):
                print(f"  btn: txt={repr(txt)}, label={repr(label)}")
        except Exception:
            pass
