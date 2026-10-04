from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    flow_page = next((p for p in browser.contexts[0].pages if 'flow.google.com' in p.url), None)
    if flow_page:
        flow_page.screenshot(path=r'C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\after_done.png')
        credits = flow_page.evaluate("""() => {
            const el = document.querySelector('flow-user-tier-chip, [aria-label*="credit"], [class*="credit"]');
            return el ? el.innerText : 'not found';
        }""")
        print("Tier / credits:", credits)
