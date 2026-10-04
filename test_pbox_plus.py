import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    flow_page = next(pg for pg in browser.contexts[0].pages if "flow.google.com" in pg.url)
    flow_page.bring_to_front()
    
    # 1. Close any open header popups
    flow_page.keyboard.press("Escape")
    time.sleep(1)
    
    # 2. Find prompt box container
    pbox = flow_page.locator(".prompt-box, flow-base-prompt-box, [class*='prompt-box']").first
    print("Prompt box found:", pbox.count())
    
    # Find all buttons strictly inside prompt box
    pbox_btns = pbox.locator("button").all()
    print("Buttons inside prompt box:", len(pbox_btns))
    for i, b in enumerate(pbox_btns):
        txt = b.inner_text().strip()
        label = b.get_attribute("aria-label") or ""
        print(f"[{i}] txt={repr(txt)}, label={repr(label)}, box={b.bounding_box()}")
        if txt == "+" or txt == "add" or "add" in label.lower() or "ingredient" in label.lower():
            print(f"--> TARGET PLUS BUTTON IS AT INDEX {i}!")
            b.click()
            time.sleep(2)
            break
            
    flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\drawer_opened_from_pbox.png")
    print("Screenshot saved to drawer_opened_from_pbox.png!")
