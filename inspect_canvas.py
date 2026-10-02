import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = [pg for pg in browser.contexts[0].pages if 'flow.google.com' in pg.url][0]
        
        # Check text elements on the page
        print("Page URL:", page.url)
        
        # Look for video cards
        cards = await page.locator("div[role='button'], div[tabindex='0']").all()
        print(f"Found {len(cards)} clickable card candidates")
        
        # Let's extract all visible text on the page
        body_text = await page.evaluate("() => document.body.innerText")
        lines = [line.strip() for line in body_text.split("\n") if line.strip()]
        print("=== PAGE LINES ===")
        for line in lines[:30]:
            print("  ", line)

asyncio.run(inspect())
