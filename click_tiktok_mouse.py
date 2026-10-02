import sys
import time
from playwright.sync_api import sync_playwright

def click_with_mouse():
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
        
        # Enable console logs
        tt_page.on("console", lambda msg: print(f"Browser Console: {msg.text}"))
        
        # Check Post button
        btn = tt_page.locator("button:text-is('Post')")
        print("btn count:", btn.count())
        if btn.count() > 0:
            box = btn.first.bounding_box()
            print("Bounding box:", box)
            x = box["x"] + box["width"] / 2
            y = box["y"] + box["height"] / 2
            print(f"Moving mouse to ({x}, {y}) and clicking...")
            tt_page.mouse.move(x, y)
            time.sleep(0.5)
            tt_page.mouse.down()
            time.sleep(0.2)
            tt_page.mouse.up()
            print("Mouse click dispatched!")
            
            # Wait up to 10 seconds checking if URL changes or modal appears
            for sec in range(10):
                time.sleep(1)
                text = tt_page.locator("body").inner_text()
                if "uploaded" in text.lower() or "manage your posts" in text.lower() or "manage" in text.lower():
                    print(f"Success text detected at {sec+1}s!")
                    break
                    
            tt_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\tiktok_mouse_click_proof.png")
            print("Screenshot saved!")

if __name__ == "__main__":
    click_with_mouse()
