import asyncio
from playwright.async_api import async_playwright

async def select():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = b.contexts[0].pages[0]
        
        overlay = page.locator('.cdk-overlay-container')
        target = overlay.locator("text='Boy and girl playing dressup'").first
        print('Overlay target count:', await target.count(), flush=True)
        if await target.count() > 0:
            await target.click()
            print('Clicked Boy and girl playing dressup!', flush=True)
            await page.wait_for_timeout(2000)
            await page.screenshot(path=r'C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\after_target_click.png')

asyncio.run(select())
