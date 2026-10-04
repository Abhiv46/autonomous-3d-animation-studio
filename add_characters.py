from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    flow_page = next((p for p in browser.contexts[0].pages if 'flow.google.com' in p.url), None)
    if flow_page:
        # In the drawer, find Kaavya
        kaavya_item = flow_page.locator("text='Kaavya'")
        print("Kaavya items found:", kaavya_item.count())
        if kaavya_item.count() > 0:
            kaavya_item.first.click()
            time.sleep(1)
            add_btn = flow_page.locator("button:has-text('Add to prompt')")
            if add_btn.count() > 0:
                add_btn.first.click()
                print("Added Kaavya!")
                time.sleep(1)
                
        # Now find Kaartik
        kaartik_item = flow_page.locator("text='Kaartik'")
        print("Kaartik items found:", kaartik_item.count())
        if kaartik_item.count() > 0:
            kaartik_item.first.click()
            time.sleep(1)
            add_btn = flow_page.locator("button:has-text('Add to prompt')")
            if add_btn.count() > 0:
                add_btn.first.click()
                print("Added Kaartik!")
                time.sleep(1)
        
        # If drawer is still open, close it with Escape or clicking backdrop
        flow_page.keyboard.press("Escape")
        time.sleep(0.5)
        
        flow_page.screenshot(path=r'C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\all_chips_ready.png')
        print("Screenshot saved!")
