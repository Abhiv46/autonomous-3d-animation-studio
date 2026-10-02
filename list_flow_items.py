import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = [pg for pg in browser.contexts[0].pages if 'flow.google.com' in pg.url][0]
        
        # Get all text inside canvas / cards
        items = await page.evaluate('''() => {
            const results = [];
            // Find all elements with aria-label or title or text
            const nodes = document.querySelectorAll('[aria-label], button, a, h1, h2, h3, h4, span');
            for (let n of nodes) {
                const label = n.getAttribute('aria-label');
                const title = n.getAttribute('title');
                const text = n.innerText ? n.innerText.trim() : '';
                if (label && label.length > 3) results.push({type: 'label', val: label});
                if (title && title.length > 3) results.push({type: 'title', val: title});
                if (text && text.length > 5 && text.length < 100) results.push({type: 'text', val: text});
            }
            return results;
        }''')
        
        seen = set()
        print("Unique found items:")
        for it in items:
            val = it['val']
            if val not in seen:
                seen.add(val)
                print(f"[{it['type']}] {val}")

asyncio.run(run())
