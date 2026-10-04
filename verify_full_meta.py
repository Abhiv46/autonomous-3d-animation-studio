import asyncio
from playwright.async_api import async_playwright

VID_ID = "j98zuoqOngk"

async def check():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = [pg for pg in b.contexts[0].pages if "studio.youtube.com" in pg.url][0]
        
        # Check description
        desc_box = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
        desc = await desc_box.inner_text() if await desc_box.count() > 0 else ""
        
        # Check title
        title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        title = await title_box.inner_text() if await title_box.count() > 0 else ""
        
        print(f"Title: {title}")
        print(f"Description length: {len(desc)} characters")
        print("Description snippet:\n", desc[:150])

if __name__ == "__main__":
    asyncio.run(check())
