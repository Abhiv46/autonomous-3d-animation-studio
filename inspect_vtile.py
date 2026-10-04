from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    flow_page = next((p for p in browser.contexts[0].pages if 'flow.google.com' in p.url), None)
    if flow_page:
        flow_page.keyboard.press('Escape')
        # Let's inspect tile [2] (first video tile)
        vtiles = flow_page.query_selector_all('flow-video-tile')
        print(f"Total video tiles: {len(vtiles)}")
        
        # Click tile [2] to see details
        if len(vtiles) > 0:
            vtiles[0].click()
            time.sleep(2)
            flow_page.screenshot(path=r'C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\vtile0_opened.png')
            # Extract prompt text from side or panel
            details = flow_page.evaluate("""() => {
                const textNodes = Array.from(document.querySelectorAll('flow-video-player, mat-card, .prompt-text, [class*="prompt"], [class*="detail"]'));
                return textNodes.map(n => n.innerText.slice(0, 150));
            }""")
            print("VT0 details:", details)
