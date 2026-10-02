import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        print(f"Contexts count: {len(b.contexts)}")
        for ci, ctx in enumerate(b.contexts):
            print(f"Context {ci}: {len(ctx.pages)} pages")
            for pi, pg in enumerate(ctx.pages):
                try:
                    print(f"  Page {pi}: {pg.url}")
                except Exception as e:
                    print(f"  Page {pi}: error {e}")
        await b.close()

asyncio.run(run())
