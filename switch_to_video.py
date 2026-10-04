from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    flow_page = next((p for p in browser.contexts[0].pages if 'flow.google.com' in p.url), None)
    if flow_page:
        # Find all overlays
        panes = flow_page.locator(".cdk-overlay-pane")
        print("Overlay count:", panes.count())
        
        # Click the button that has text 'Video' inside the overlay pane that contains 'Image'
        target_pane = None
        for i in range(panes.count()):
            p_elem = panes.nth(i)
            if "Image" in p_elem.inner_text() and "Video" in p_elem.inner_text():
                target_pane = p_elem
                break
        
        if target_pane:
            print("Found target pane!")
            # Find the Video button
            vid_btn = target_pane.locator("button, [role='button'], [role='tab'], mat-button-toggle").filter(has_text="Video")
            print("Video buttons in pane:", vid_btn.count())
            if vid_btn.count() > 0:
                vid_btn.first.click()
                print("Clicked Video button!")
            else:
                # Try clicking via coordinates or javascript
                target_pane.evaluate("""pane => {
                    const btns = Array.from(pane.querySelectorAll('button, div, span')).filter(el => el.innerText.trim() === 'Video');
                    if (btns.length > 0) btns[0].click();
                }""")
                print("Clicked via evaluate!")
            time.sleep(1)
            
            # Select 9:16 vertical ratio if available
            ratio_9_16 = target_pane.locator("button, [role='button']").filter(has_text="9:16")
            if ratio_9_16.count() > 0:
                ratio_9_16.first.click()
                print("Selected 9:16!")
            
            flow_page.keyboard.press("Escape")
            time.sleep(0.5)
            
        flow_page.screenshot(path=r'C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\after_mode_switched.png')
        print("Screenshot saved after mode switch!")
