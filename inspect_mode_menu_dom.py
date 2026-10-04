from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    flow_page = next(pg for pg in browser.contexts[0].pages if "flow.google.com" in pg.url)
    
    # 1. Click the mode button to open the menu
    for b in flow_page.locator("button").all():
        txt = b.inner_text().strip()
        if "video" in txt.lower() or "720p" in txt.lower():
            print(f"Clicking mode trigger: {txt}")
            b.click()
            break
            
    flow_page.wait_for_timeout(1000)
    
    # 2. Inspect all elements with text 'Image'
    imgs = flow_page.locator("text='Image'").all()
    print(f"Elements with text 'Image': {len(imgs)}")
    for i, el in enumerate(imgs):
        tag = el.evaluate("e => e.tagName")
        cls = el.evaluate("e => e.className")
        parent = el.evaluate("e => e.parentElement ? e.parentElement.outerHTML.slice(0, 150) : ''")
        box = el.bounding_box()
        print(f"[{i}] tag={tag}, box={box}\n    parent={parent}")
