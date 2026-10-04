from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    
    # Check all file inputs
    inputs = page.locator("input[type='file']").all()
    print("Found file inputs:", len(inputs))
    for i, inp in enumerate(inputs):
        print(f"Input {i}: outerHTML =", inp.evaluate("el => el.outerHTML"))
