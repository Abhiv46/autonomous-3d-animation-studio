from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    flow_page = next((p for p in browser.contexts[0].pages if 'flow.google.com' in p.url), None)
    if flow_page:
        # Click the '+' button inside prompt box
        add_btn = flow_page.locator("flow-base-prompt-box button, .prompt-box button").filter(has=flow_page.locator("mat-icon:has-text('add')"))
        print("Found add button:", add_btn.count())
        add_btn.first.click()
        time.sleep(1.5)
        
        flow_page.screenshot(path=r'C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\drawer_opened.png')
        
        # Check what tabs or sections are inside the drawer
        drawer_info = flow_page.evaluate("""() => {
            const drawer = document.querySelector('mat-sidenav[opened], .drawer, [class*="drawer"]');
            if (!drawer) return 'No drawer';
            const tabs = Array.from(drawer.querySelectorAll('button, [role="tab"], .mat-tab-label, mat-list-item'));
            return tabs.map(t => ({
                text: t.innerText.replace(/\\s+/g, ' ').trim(),
                box: t.getBoundingClientRect()
            })).filter(t => t.text.length > 0);
        }""")
        print("Drawer tabs/buttons:", drawer_info)
