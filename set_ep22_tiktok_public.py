import sys
import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pg = browser.contexts[0].pages[0]
        
        # Check if Private dropdown is clickable
        priv_btn = pg.locator("button:has-text('Private')").first
        if priv_btn.count() > 0:
            print("Private button found!")
            priv_btn.click(force=True)
            time.sleep(1)
            pub_opt = pg.locator("li:has-text('Public'), [role='option']:has-text('Public'), div:has-text('Public')").first
            if pub_opt.count() > 0:
                print("Public option found, clicking...")
                pub_opt.click(force=True)
                time.sleep(2)
            else:
                print("Public option not in list, might still be under automated review.")
        else:
            print("No Private button found (already Public or processing).")
            
        pg.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\tiktok_privacy_check.png")
        print("Done!")

if __name__ == "__main__":
    main()
