from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    flow_page = next((p for p in browser.contexts[0].pages if 'flow.google.com' in p.url), None)
    if flow_page:
        # Click Done to go back to canvas
        done_btn = flow_page.locator("button:has-text('Done')")
        if done_btn.count() > 0:
            done_btn.first.click()
        
        # Check credits banner or header
        banner = flow_page.locator("flow-credit-banner, [class*='credit']").all_inner_texts()
        print("Credits:", banner)
