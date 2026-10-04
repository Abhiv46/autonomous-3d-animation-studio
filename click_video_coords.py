from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    flow_page = next(pg for pg in browser.contexts[0].pages if "flow.google.com" in pg.url)
    flow_page.bring_to_front()
    
    # Click at coordinates of [Video] toggle: x=485, y=508
    print("Clicking Video toggle at (485, 508)...")
    flow_page.mouse.click(485, 508)
    time.sleep(1)
    
    # Take screenshot of popover to see if Video is now selected
    flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\after_coords_click_video.png")
    print("Screenshot saved to after_coords_click_video.png!")
