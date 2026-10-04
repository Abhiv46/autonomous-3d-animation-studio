from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    flow_page = next((p for p in browser.contexts[0].pages if 'flow.google.com' in p.url), None)
    if flow_page:
        flow_page.keyboard.press('Escape')
        # Let's inspect custom elements in flow
        tags = flow_page.evaluate("""() => {
            const all = Array.from(document.querySelectorAll('*'));
            const custom = new Set();
            all.forEach(el => {
                if (el.tagName.includes('-') || el.tagName.toLowerCase().includes('card') || el.tagName.toLowerCase().includes('tile')) {
                    custom.add(el.tagName.toLowerCase());
                }
            });
            return Array.from(custom);
        }""")
        print("Custom tags:", tags)
