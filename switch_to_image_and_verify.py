import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    flow_page = next(pg for pg in browser.contexts[0].pages if "flow.google.com" in pg.url)
    flow_page.bring_to_front()
    
    # 1. Locate the button with 'Video' or '720p'
    mode_btn = None
    for b in flow_page.locator("button").all():
        txt = b.inner_text().strip()
        if "video" in txt.lower() or "720p" in txt.lower():
            mode_btn = b
            print(f"[+] Found mode button: {txt}")
            break
            
    if mode_btn:
        mode_btn.click()
        time.sleep(1)
        
    flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\popover_open_check.png")
    
    # 2. Look for the mat-button-toggle or button containing 'Image'
    # We saw in DOM: <span class="toggle-label"> with text 'Image'
    # Let's find the button toggle
    toggles = flow_page.locator("mat-button-toggle, [role='button'], button").all()
    img_clicked = False
    for t in toggles:
        txt = t.inner_text().strip()
        if "image" in txt.lower() and "video" not in txt.lower():
            print(f"[+] Clicking Image toggle: {repr(txt)}")
            t.click(force=True)
            img_clicked = True
            time.sleep(1)
            break
            
    if not img_clicked:
        print("[!] Trying text='Image' directly...")
        flow_page.locator("text='Image'").first.click(force=True)
        time.sleep(1)
        
    # Check 9:16 aspect ratio
    v916 = flow_page.locator("mat-button-toggle:has-text('9:16'), button:has-text('9:16')").first
    if v916.count() > 0:
        print("[+] Clicking 9:16 toggle...")
        v916.click(force=True)
        time.sleep(0.5)
        
    # Close popover by pressing Escape
    flow_page.keyboard.press("Escape")
    time.sleep(1)
    
    # Check prompt box badge text
    prompt_box_text = flow_page.locator(".prompt-box, flow-base-prompt-box, [class*='prompt']").first.inner_text()
    print("--- Prompt box text snippet ---")
    print(prompt_box_text)
    print("-------------------------------")
    
    flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\after_image_toggle_proof.png")
    print("Screenshot saved to after_image_toggle_proof.png!")
