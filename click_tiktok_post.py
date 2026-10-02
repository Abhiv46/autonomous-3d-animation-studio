import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def click_post():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        tt_page = None
        for pg in context.pages:
            if "tiktok.com" in pg.url:
                tt_page = pg
                break
                
        if not tt_page:
            print("No TikTok page found!")
            return

        print("Found TikTok page:", tt_page.url)
        tt_page.bring_to_front()
        
        # Look for buttons
        btns = tt_page.locator("button")
        count = btns.count()
        print(f"Total buttons on page: {count}")
        for i in range(count):
            txt = btns.nth(i).inner_text().strip()
            if "post" in txt.lower():
                print(f"Button {i}: '{txt}'")
                box = btns.nth(i).bounding_box()
                print(f"Bounding box: {box}")
                if box and box["width"] > 0:
                    print(f"Clicking Post button at index {i}...")
                    btns.nth(i).click(force=True)
                    time.sleep(4)
                    break
                    
        # Check if manage posts or confirmation appeared
        time.sleep(3)
        tt_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\tiktok_after_post_click.png")
        print("Screenshot after post click saved!")

if __name__ == "__main__":
    click_post()
