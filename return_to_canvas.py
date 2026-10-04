from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    flow_page = next(pg for pg in browser.contexts[0].pages if "flow.google.com" in pg.url)
    flow_page.bring_to_front()
    
    done = flow_page.locator("button:has-text('Done')").first
    if done.count() > 0:
        done.click()
    else:
        # Click back arrow
        back = flow_page.locator("button:has-text('arrow_back'), [aria-label*='Back']").first
        if back.count() > 0:
            back.click()
        else:
            flow_page.keyboard.press("Escape")
            
    time.sleep(1.5)
    flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\back_to_canvas.png")
    print("Screenshot saved!")
