import sys
import time
from playwright.sync_api import sync_playwright

def post_now():
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

        tt_page.bring_to_front()
        
        # Click button 25 ('Post')
        btns = tt_page.locator("button")
        target_btn = None
        for i in range(btns.count()):
            txt = btns.nth(i).inner_text().strip()
            if txt == "Post":
                target_btn = btns.nth(i)
                print(f"Found exact 'Post' button at index {i}!")
                break
                
        if target_btn:
            box = target_btn.bounding_box()
            print(f"Post button bounding box: {box}")
            # Scroll to button and click
            target_btn.scroll_into_view_if_needed()
            time.sleep(1)
            target_btn.click(force=True)
            print("Clicked Post button!")
            time.sleep(6)
            
            # Check for any post modal or success
            tt_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\tiktok_final_posted_proof.png")
            print("Final screenshot saved!")
        else:
            print("Post button not found!")

if __name__ == "__main__":
    post_now()
