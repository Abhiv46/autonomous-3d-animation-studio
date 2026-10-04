import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = [pg for pg in b.contexts[0].pages if "studio.youtube.com" in pg.url][0]
        boxes = await page.locator("[contenteditable='true'], #textbox").all()
        print("Total editable boxes:", len(boxes))
        for i, box in enumerate(boxes):
            aria = await box.get_attribute("aria-label")
            id_val = await box.get_attribute("id")
            parent = await box.evaluate("el => el.parentElement ? el.parentElement.tagName + '.' + el.parentElement.className : 'none'")
            print(f"Box {i+1}: id={id_val}, aria={aria}, parent={parent}")

if __name__ == "__main__":
    asyncio.run(inspect())
