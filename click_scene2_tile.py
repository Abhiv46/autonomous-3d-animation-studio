import asyncio
from playwright.async_api import async_playwright

async def click_tile():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = b.contexts[0].pages[0]
        
        # Click on Child wearing giant high heels
        tile = page.locator("[aria-label*='Child wearing giant high heels']").first
        if await tile.count() == 0:
            tile = page.get_by_text("Child wearing gi").first
            
        print("Tile count:", await tile.count(), flush=True)
        if await tile.count() > 0:
            await tile.click()
            await page.wait_for_timeout(3000)
            print("New URL:", page.url, flush=True)
            await page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\after_scene2_tile_click.png")

asyncio.run(click_tile())
