import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = b.contexts[0].pages[0]
        
        # Scroll up to top of canvas
        await page.mouse.wheel(0, -1000)
        await page.wait_for_timeout(2000)
        await page.screenshot(path=r'C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\top_tiles.png')
        
        # Check credits remaining
        btn = page.get_by_role('button', name='Account details')
        if await btn.count() > 0:
            await btn.click()
            await page.wait_for_timeout(1000)
            text = await page.locator("div[role='dialog'], [role='menu'], div[class*='panel']").all_inner_texts()
            for t in text:
                for line in t.split("\n"):
                    if "credit" in line.lower():
                        print("Credit line:", line)
            await page.keyboard.press('Escape')

asyncio.run(inspect())
