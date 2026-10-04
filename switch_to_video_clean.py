import sys
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    flow_page = next(pg for pg in browser.contexts[0].pages if "flow.google.com" in pg.url)
    flow_page.bring_to_front()
    
    # Click the Video button inside overlay
    # In screenshot: [Image] is on left, [Video] is on right
    # Overlay is already open!
    overlay = flow_page.locator(".cdk-overlay-pane").first
    print("Overlay visible:", overlay.is_visible())
    
    # Target the 'Video' button toggle
    video_btn = overlay.locator("mat-button-toggle:has-text('Video'), button:has-text('Video'), div:has-text('Video')").first
    # Find exact toggle
    for t in overlay.locator("mat-button-toggle, [role='button'], button").all():
        if "video" in t.inner_text().lower() and "image" not in t.inner_text().lower():
            video_btn = t
            print("Found exact video toggle:", repr(t.inner_text()))
            break
            
    video_btn.click(force=True)
    time.sleep(1)
    
    # Click 9:16
    for t in overlay.locator("mat-button-toggle, [role='button'], button").all():
        if "9:16" in t.inner_text():
            t.click(force=True)
            print("Selected 9:16 vertical ratio!")
            time.sleep(0.5)
            break
            
    # Dismiss overlay
    flow_page.keyboard.press("Escape")
    time.sleep(1)
    
    flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\video_mode_confirmed.png")
    print("Saved video_mode_confirmed.png!")
