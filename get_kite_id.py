import asyncio
from playwright.async_api import async_playwright

async def get_id():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = [pg for pg in b.contexts[0].pages if "studio.youtube.com" in pg.url][0]
        rows = await page.locator("ytcp-video-row").all()
        for i, r in enumerate(rows[:4]):
            t = await r.locator("#video-title").inner_text()
            links = await r.locator("a").evaluate_all("elements => elements.map(e => e.href)")
            print(f"Row {i+1}:", t.encode("ascii", "replace").decode(), links)

if __name__ == "__main__":
    asyncio.run(get_id())
