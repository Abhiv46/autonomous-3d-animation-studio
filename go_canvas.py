import asyncio
from playwright.async_api import async_playwright

async def go_canvas():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = b.contexts[0].pages[0]
        
        # Click Done or back or navigate
        done = page.locator("button:has-text('Done'), button:has(mat-icon:has-text('check'))").first
        if await done.count() > 0 and await done.is_visible():
            await done.click()
            await page.wait_for_timeout(2000)
        else:
            await page.goto("https://flow.google.com/u/2/project/0fa549b9-b73f-4dac-8061-365fd0498eb2")
            await page.wait_for_timeout(3000)
            
        print("Back to canvas. URL:", page.url, flush=True)

asyncio.run(go_canvas())
