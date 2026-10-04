import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    
    # Inspect buttons in the first draft row
    draft_row = page.locator("ytcp-video-row").nth(1)
    buttons = draft_row.locator("button, ytcp-button, a").all()
    print("Buttons in draft row:", len(buttons))
    for i, b in enumerate(buttons):
        print(f"Btn {i}: text='{b.inner_text().strip()}', aria='{b.get_attribute('aria-label')}'")
