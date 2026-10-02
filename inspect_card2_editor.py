import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = [pg for pg in browser.contexts[0].pages if 'flow.google.com' in pg.url][0]
        
        card = page.locator("[aria-label*='Toddler walking in oversized shoes']").first
        if await card.count() > 0:
            print("Found card with aria-label, clicking...", flush=True)
            await card.click()
            await page.wait_for_timeout(3000)
            print("Page URL:", page.url, flush=True)
            await page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\card2_editor.png")
            print("Saved card2_editor.png", flush=True)
        else:
            print("Card not found by aria-label", flush=True)

asyncio.run(check())
