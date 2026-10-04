import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    flow_page = next(pg for pg in browser.contexts[0].pages if "flow.google.com" in pg.url)
    flow_page.bring_to_front()
    
    # Find More options buttons
    more_btns = flow_page.locator("button[aria-label='More options']").all()
    print("Found 'More options' buttons:", len(more_btns))
    if more_btns:
        print("Clicking first 'More options' button (Tile 1)...")
        more_btns[0].click()
        time.sleep(1)
        
    flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\more_options_menu_opened.png")
    
    # Print menu items
    menu_items = flow_page.locator("[role='menuitem'], button, span, div").all()
    print("Menu items in open menu:")
    for m in menu_items:
        try:
            t = m.inner_text().strip()
            if t in ["Animate", "Create video", "Download", "Delete", "Add to prompt", "Use as reference", "Edit", "Upscale"]:
                print(f"  [+] Option: {repr(t)}")
        except Exception:
            pass
