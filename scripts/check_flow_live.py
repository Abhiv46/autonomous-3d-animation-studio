import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp('http://localhost:9222')
            context = browser.contexts[0]
            print(f"Connected! Total pages: {len(context.pages)}")
            flow_page = None
            for pg in context.pages:
                if 'flow' in pg.url:
                    flow_page = pg
                    break
            if not flow_page:
                print("No Google Flow page found!")
                return

            print(f"Flow Page URL: {flow_page.url}")
            await flow_page.screenshot(path='scripts/flow_current_status.png')
            print("Saved screenshot to scripts/flow_current_status.png")

            # Check stop button
            stop_btn = await flow_page.query_selector('button:has-text("Stop"), button:has-text("stop")')
            print(f"Stop button present: {stop_btn is not None}")

            # Check video tags
            videos = await flow_page.query_selector_all('video')
            print(f"Video elements on page: {len(videos)}")
            for idx, v in enumerate(videos):
                src = await v.get_attribute('src')
                print(f"Video {idx} src: {src}")

            # Check text elements
            body_text = await flow_page.inner_text('body')
            # Look for progress or error messages
            for line in body_text.split('\n'):
                line_clean = line.strip()
                if any(w in line_clean.lower() for w in ['generating', 'error', 'failed', 'credit', 'limit', 'download', 'progress', '%', 'render']):
                    print(f"Relevant text: {line_clean}")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(check())
