import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pg = browser.contexts[0].pages[0]
        
        # Listen to requests
        pg.on("request", lambda req: print(f"REQ: {req.method} {req.url[:100]}"))
        pg.on("response", lambda res: print(f"RES: {res.status} {res.url[:100]}"))
        
        btn = pg.locator("button[data-e2e='post_video_button']")
        print(f"Found post button: {btn.count()}")
        
        # Scroll to button
        btn.scroll_into_view_if_needed()
        time.sleep(1)
        
        print("Clicking post button...")
        btn.click()
        
        # Wait 8 seconds
        time.sleep(8)
        
        # Check screenshot
        screenshot_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\tiktok_after_pg_click.png"
        pg.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

if __name__ == "__main__":
    main()
