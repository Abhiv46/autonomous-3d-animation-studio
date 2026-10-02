from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    for pg in context.pages:
        if "tiktok.com" in pg.url:
            print("Current URL:", pg.url)
            pg.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\tiktok_current_state.png")
            texts = pg.locator("body").inner_text()
            print("Page Text snippet:\n", texts[:500])
