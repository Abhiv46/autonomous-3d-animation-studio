import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Try clicking close button or pressing Escape
    close_btn = page.locator("button:has-text('Close'), button[aria-label='Close'], button[aria-label*='close' i]").first
    if close_btn.count() > 0 and close_btn.is_visible():
        print("[+] Clicking Close button on overlay...")
        close_btn.click(force=True)
        page.wait_for_timeout(2000)
    else:
        print("[+] Pressing Escape key...")
        page.keyboard.press("Escape")
        page.wait_for_timeout(2000)

    # Now navigate directly to The Naughty Duo project URL
    print("[+] Navigating to 'The Naughty Duo' project...")
    page.goto("https://flow.google.com/u/0/project/1876f0f7-bc42-4764-86c9-35d76cb3a615")
    page.wait_for_timeout(6000)

    print("[+] Active URL:", page.url)
    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\project_canvas_live.png")
