from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    flow_page = next((p for p in browser.contexts[0].pages if 'flow.google.com' in p.url), None)
    if flow_page:
        flow_page.keyboard.press('Escape')
        time.sleep(0.5)
        
        # Click the model toggle button on prompt box
        badge = flow_page.locator("flow-base-prompt-box button:has-text('Banana'), flow-base-prompt-box button:has-text('Nano'), .prompt-box button:has-text('Banana')")
        if badge.count() == 0:
            badge = flow_page.locator(".prompt-box button, flow-base-prompt-box button").filter(has_text="x1")
        print("Found badge:", badge.count())
        badge.first.click()
        time.sleep(1)
        
        # Screenshot overlay
        flow_page.screenshot(path=r'C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\popover_opened_live.png')
        
        # Let's inspect elements inside .cdk-overlay-pane
        overlay_elements = flow_page.evaluate("""() => {
            const pane = document.querySelector('.cdk-overlay-pane');
            if (!pane) return 'No pane';
            const buttons = Array.from(pane.querySelectorAll('button, mat-button-toggle, [role="button"], [role="radio"]'));
            return buttons.map(b => ({
                tag: b.tagName,
                text: b.innerText.replace(/\\s+/g, ' ').trim(),
                aria: b.getAttribute('aria-label') || '',
                box: b.getBoundingClientRect()
            }));
        }""")
        print("Overlay buttons:", overlay_elements)
