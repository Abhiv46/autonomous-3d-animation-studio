import asyncio
from playwright.async_api import async_playwright

async def inspect_more():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = b.contexts[0].pages[0]
        
        # Click more_vert
        more_btn = page.locator("button:has-text('more_vert'), button[aria-label*='More'], mat-icon:has-text('more_vert')").first
        print("More btn count:", await more_btn.count(), flush=True)
        if await more_btn.count() > 0:
            await more_btn.click()
            await page.wait_for_timeout(1000)
            
            menu_items = await page.locator("div[role='menu'], [role='menuitem'], .cdk-overlay-pane button").all_inner_texts()
            print("Menu items:", menu_items, flush=True)
            await page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\more_menu.png")

asyncio.run(inspect_more())
