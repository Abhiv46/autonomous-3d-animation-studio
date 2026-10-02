import asyncio
import urllib.request
from playwright.async_api import async_playwright

async def download_video():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = [pg for pg in browser.contexts[0].pages if 'flow.google.com' in pg.url][0]
        
        # Check download buttons
        buttons = await page.locator("button").all()
        print(f"Total buttons: {len(buttons)}", flush=True)
        
        # Look for download button
        download_btn = page.locator("button[aria-label*='Download'], button[aria-label*='download'], button:has-text('Download')").first
        has_btn = await download_btn.count() > 0
        print(f"Download button found: {has_btn}", flush=True)
        
        if has_btn:
            async with page.expect_download() as download_info:
                await download_btn.click()
            download = await download_info.value
            save_path = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips\card2_oversized_shoes.mp4"
            await download.save_as(save_path)
            print(f"Downloaded video successfully to {save_path}", flush=True)
        else:
            # Let's inspect header buttons
            for i, b in enumerate(buttons):
                label = await b.get_attribute("aria-label")
                text = await b.inner_text()
                if label or text:
                    print(f"Btn {i}: label='{label}', text='{text}'", flush=True)

asyncio.run(download_video())
