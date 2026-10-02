import asyncio
from playwright.async_api import async_playwright

async def inspect_tile():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = browser.contexts[0].pages[0]
        
        # Hover over Tile 3: Boy and girl playing dressup
        tile = page.locator("[aria-label*='Boy and girl playing']").first
        print("Tile count:", await tile.count(), flush=True)
        if await tile.count() > 0:
            print("Hovering on tile...", flush=True)
            await tile.hover()
            await page.wait_for_timeout(1000)
            
            # Check buttons that appeared on hover
            btns = await page.locator(".cdk-overlay-pane, [role='button'], button").all()
            for b in btns:
                lbl = await b.get_attribute("aria-label")
                txt = await b.inner_text()
                if lbl or (txt and len(txt) < 30):
                    if any(w in (lbl or '').lower() or w in txt.lower() for w in ['prompt', 'add', 'favorite', 'more']):
                        print(f"Hover button: label='{lbl}', text='{txt}'", flush=True)

asyncio.run(inspect_tile())
