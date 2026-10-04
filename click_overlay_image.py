import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    flow_page = next(pg for pg in browser.contexts[0].pages if "flow.google.com" in pg.url)
    flow_page.bring_to_front()
    
    # 1. First make sure popover is open
    overlay = flow_page.locator(".cdk-overlay-pane, [class*='overlay-pane'], [class*='popover']").first
    if overlay.count() == 0 or not overlay.is_visible():
        print("[+] Opening mode menu...")
        for b in flow_page.locator("button").all():
            txt = b.inner_text().strip()
            if "video" in txt.lower() or "720p" in txt.lower():
                b.click()
                break
        time.sleep(1)
        overlay = flow_page.locator(".cdk-overlay-pane, [class*='overlay-pane'], [class*='popover']").first

    print(f"Overlay visible: {overlay.is_visible()}")
    
    # 2. Click the Image toggle inside overlay
    # Find all elements inside overlay
    for el in overlay.locator("button, mat-button-toggle, [role='button'], div, span").all():
        txt = el.inner_text().strip()
        if txt == "Image" or (txt.startswith("Image") and "video" not in txt.lower()):
            box = el.bounding_box()
            print(f"[+] Found Image inside overlay! Text={repr(txt)}, Box={box}")
            el.click(force=True)
            time.sleep(1)
            break
            
    # 3. Click 9:16 inside overlay
    for el in overlay.locator("button, mat-button-toggle, [role='button'], div, span").all():
        txt = el.inner_text().strip()
        if "9:16" in txt:
            print(f"[+] Clicking 9:16 inside overlay! Text={repr(txt)}")
            el.click(force=True)
            time.sleep(0.5)
            break
            
    # Close overlay
    flow_page.keyboard.press("Escape")
    time.sleep(1)
    
    flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\overlay_after_image_click.png")
    
    # Check what mode badge is now showing in the prompt box
    for b in flow_page.locator("button").all():
        txt = b.inner_text().strip()
        if any(w in txt.lower() for w in ["image", "video", "banana", "veo", "9:16"]):
            print(f"--> Current Badge: {repr(txt)}")
