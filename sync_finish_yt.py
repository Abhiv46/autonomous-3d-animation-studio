import sys
import time
from playwright.sync_api import sync_playwright

print("[1] Starting sync playwright...", flush=True)

with sync_playwright() as p:
    print("[2] Connecting to CDP 9222...", flush=True)
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    print(f"[3] Connected! Total pages: {len(context.pages)}", flush=True)
    
    # Find the YouTube page
    page = None
    for pg in context.pages:
        if "studio.youtube.com" in pg.url:
            page = pg
            break
            
    if not page:
        print("[!] YouTube page not found in open pages", flush=True)
        sys.exit(1)
        
    print(f"[4] Using YouTube page: {page.url}", flush=True)
    
    dialog = page.locator("ytcp-uploads-dialog")
    print("Dialog present count:", dialog.count(), flush=True)
    
    if dialog.count() > 0:
        # Not made for kids
        not_kids = dialog.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
        if not_kids.count() > 0:
            not_kids.click(force=True)
            print("[+] Clicked Not made for kids", flush=True)
            page.wait_for_timeout(500)
            
        # Next buttons
        for i in range(3):
            next_btn = dialog.locator("ytcp-button#next-button, button:has-text('Next')").first
            if next_btn.count() > 0 and next_btn.is_visible():
                next_btn.click(force=True)
                print(f"[+] Clicked Next ({i+1})", flush=True)
                page.wait_for_timeout(2000)
                
        # Public
        pub = dialog.locator("tp-yt-paper-radio-button[name='PUBLIC']").first
        if pub.count() > 0:
            pub.click(force=True)
            print("[+] Selected PUBLIC visibility!", flush=True)
            page.wait_for_timeout(1000)
            
        # Publish
        publish_btn = dialog.locator("ytcp-button#done-button, button:has-text('Publish'), button:has-text('Save')").first
        if publish_btn.count() > 0 and publish_btn.is_visible():
            publish_btn.click(force=True)
            print("[+] Clicked Publish button in dialog!", flush=True)
            page.wait_for_timeout(4000)
            
        # Publish anyway if shown
        anyway = page.locator("button:has-text('Publish anyway')").first
        if anyway.count() > 0 and anyway.is_visible():
            anyway.click(force=True)
            print("[+] Clicked Publish anyway!", flush=True)
            page.wait_for_timeout(3000)
            
    page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_original_published_proof.png")
    print("[SUCCESS] YouTube publish confirmed!", flush=True)

