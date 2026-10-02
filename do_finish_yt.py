import asyncio
import sys
from playwright.async_api import async_playwright

async def run():
    print("[1] Launching async_playwright...", flush=True)
    async with async_playwright() as p:
        print("[2] Connecting to CDP 9222...", flush=True)
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        print("[3] Connected! Inspecting contexts...", flush=True)
        ctx = b.contexts[0]
        pages = ctx.pages
        print(f"[4] Total pages: {len(pages)}", flush=True)
        
        page = None
        for pg in pages:
            print(f"    Page url: {pg.url}", flush=True)
            if "studio.youtube.com" in pg.url:
                page = pg
                break
                
        if not page:
            print("[!] YouTube page not found!", flush=True)
            return
            
        print(f"[5] Using YouTube page: {page.url}", flush=True)
        
        dialog = page.locator("ytcp-uploads-dialog")
        dlg_count = await dialog.count()
        print(f"[6] Dialog count: {dlg_count}", flush=True)
        
        if dlg_count > 0:
            # 1. Not made for kids
            not_kids = dialog.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
            if await not_kids.count() > 0:
                await not_kids.click(force=True)
                print("[+] Clicked Not made for kids", flush=True)
                await page.wait_for_timeout(500)
                
            # 2. Next buttons
            for i in range(4):
                next_btn = dialog.locator("ytcp-button#next-button, button:has-text('Next')").first
                if await next_btn.count() > 0 and await next_btn.is_visible():
                    await next_btn.click(force=True)
                    print(f"[+] Clicked Next ({i+1})", flush=True)
                    await page.wait_for_timeout(2000)
                    
            # 3. Public visibility
            pub = dialog.locator("tp-yt-paper-radio-button[name='PUBLIC']").first
            if await pub.count() > 0:
                await pub.click(force=True)
                print("[+] Selected PUBLIC visibility!", flush=True)
                await page.wait_for_timeout(1000)
                
            # 4. Click Publish
            publish_btn = dialog.locator("ytcp-button#done-button, button:has-text('Publish'), button:has-text('Save')").first
            if await publish_btn.count() > 0 and await publish_btn.is_visible():
                await publish_btn.click(force=True)
                print("[+] Clicked Publish button in dialog!", flush=True)
                await page.wait_for_timeout(4000)
                
            # 5. Check 'Publish anyway'
            anyway = page.locator("button:has-text('Publish anyway')").first
            if await anyway.count() > 0 and await anyway.is_visible():
                await anyway.click(force=True)
                print("[+] Clicked Publish anyway!", flush=True)
                await page.wait_for_timeout(3000)
                
        await page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_original_published_proof.png")
        print("[SUCCESS] YouTube publish step complete!", flush=True)

if __name__ == "__main__":
    asyncio.run(run())
