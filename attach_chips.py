from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    flow_page = next((p for p in browser.contexts[0].pages if 'flow.google.com' in p.url), None)
    if flow_page:
        # 1. Click 'Add to prompt' for the currently selected image
        add_btn = flow_page.locator("button:has-text('Add to prompt')")
        if add_btn.count() > 0:
            add_btn.first.click()
            print("Added Image to prompt!")
            time.sleep(1)
        
        # 2. Click '+' to open drawer again for Characters
        plus_btn = flow_page.locator("flow-base-prompt-box button, .prompt-box button").filter(has=flow_page.locator("mat-icon:has-text('add')"))
        if plus_btn.count() > 0:
            plus_btn.first.click()
            time.sleep(1)
            
            # Click 'Characters' inside drawer
            # Find the drawer element
            drawer = flow_page.locator(".cdk-overlay-pane, [class*='dialog'], [class*='drawer'], [class*='overlay']").filter(has_text="Search assets")
            if drawer.count() > 0:
                char_tab = drawer.locator("button, [role='button'], div, span").filter(has_text="Characters")
                print("Found characters tab:", char_tab.count())
                if char_tab.count() > 0:
                    char_tab.first.click()
                    time.sleep(1)
                    
                    # Select Kaavya
                    kaavya = drawer.locator("text='Kaavya'")
                    if kaavya.count() > 0:
                        kaavya.first.click()
                        time.sleep(0.5)
                        add_char_btn = drawer.locator("button:has-text('Add to prompt')")
                        if add_char_btn.count() > 0:
                            add_char_btn.first.click()
                            print("Added Kaavya to prompt!")
                            time.sleep(1)
        
        # 3. Click '+' again for Kaartik
        plus_btn = flow_page.locator("flow-base-prompt-box button, .prompt-box button").filter(has=flow_page.locator("mat-icon:has-text('add')"))
        if plus_btn.count() > 0:
            plus_btn.first.click()
            time.sleep(1)
            drawer = flow_page.locator(".cdk-overlay-pane, [class*='dialog'], [class*='drawer'], [class*='overlay']").filter(has_text="Search assets")
            if drawer.count() > 0:
                char_tab = drawer.locator("button, [role='button'], div, span").filter(has_text="Characters")
                if char_tab.count() > 0:
                    char_tab.first.click()
                    time.sleep(1)
                    kaartik = drawer.locator("text='Kaartik'")
                    if kaartik.count() > 0:
                        kaartik.first.click()
                        time.sleep(0.5)
                        add_char_btn = drawer.locator("button:has-text('Add to prompt')")
                        if add_char_btn.count() > 0:
                            add_char_btn.first.click()
                            print("Added Kaartik to prompt!")
                            time.sleep(1)
        
        flow_page.screenshot(path=r'C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\chips_attached_proof.png')
        print("Screenshot saved!")
