import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    flow_page = next(pg for pg in browser.contexts[0].pages if "flow.google.com" in pg.url)
    
    # 1. Click mode trigger
    for b in flow_page.locator("button").all():
        txt = b.inner_text().strip()
        if "video" in txt.lower() or "720p" in txt.lower():
            print(f"Clicking mode trigger: {txt}")
            b.click()
            break
            
    flow_page.wait_for_timeout(1000)
    
    # 2. Click the Image toggle
    img_toggle = flow_page.locator("text='Image'").first
    print("Clicking Image toggle...")
    img_toggle.click(force=True)
    flow_page.wait_for_timeout(1000)
    
    # 3. Dismiss menu
    flow_page.keyboard.press("Escape")
    flow_page.wait_for_timeout(1000)
    
    # 4. Check prompt box buttons
    print("Checking prompt box buttons after switching:")
    btns = flow_page.locator("button").all()
    for b in btns:
        txt = b.inner_text().strip()
        if any(w in txt.lower() for w in ["video", "image", "banana", "veo", "720p"]):
            print("  Badge found:", repr(txt))
            
    flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\after_image_mode_switch.png")
    print("Screenshot saved to after_image_mode_switch.png!")
