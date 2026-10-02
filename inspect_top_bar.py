import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = b.contexts[0].pages[0]
        
        info = await page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button, [role="button"], mat-icon, flow-icon'));
            return btns.map(b => ({
                tag: b.tagName,
                text: (b.innerText || '').trim(),
                aria: b.getAttribute('aria-label'),
                title: b.getAttribute('title'),
                classes: b.className
            }));
        }""")
        for item in info:
            if any([item['aria'], item['title'], item['text']]):
                print(item)

asyncio.run(inspect())
