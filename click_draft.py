import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    
    # Click the draft title
    target = page.locator("text='TheNaughtyDuo GoodHabits Master'").first
    print("Found target:", target.count())
    target.click()
    time.sleep(3)
    
    page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\after_draft_click.png")
    print("Screenshot saved! URL:", page.url)
