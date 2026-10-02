import asyncio
from playwright.async_api import async_playwright

async def download_card2():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = browser.contexts[0].pages[0]
        
        url = "https://flow.google.com/u/2/project/0fa549b9-b73f-4dac-8061-365fd0498eb2/edit/327c518b-9e97-4188-ae75-46d55a18aaf7"
        print("Navigating to:", url, flush=True)
        await page.goto(url)
        await page.wait_for_timeout(4000)
        
        # Look for the download button: it's next to heart and share
        # Let's inspect buttons in header
        header_buttons = await page.locator("header button, div[role='toolbar'] button, div.header button").all()
        print(f"Header buttons count: {len(header_buttons)}", flush=True)
        
        # Or look for button containing download icon (svg with download path)
        dl_button = None
        for btn in await page.locator("button").all():
            label = await btn.get_attribute("aria-label")
            tooltip = await btn.get_attribute("title")
            if label and "download" in label.lower():
                dl_button = btn
                print("Found download button by aria-label:", label, flush=True)
                break
            if tooltip and "download" in tooltip.lower():
                dl_button = btn
                print("Found download button by title:", tooltip, flush=True)
                break
        
        if not dl_button:
            # Let's check all button aria-labels
            for i, btn in enumerate(await page.locator("button").all()):
                lbl = await btn.get_attribute("aria-label")
                txt = await btn.inner_text()
                if lbl or txt:
                    print(f"Btn {i}: label='{lbl}', text='{txt}'", flush=True)
        else:
            save_path = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips\ep21_highheels_scene2_raw.mp4"
            print("Triggering download...", flush=True)
            async with page.expect_download(timeout=30000) as dl_info:
                await dl_button.click()
            download = await dl_info.value
            await download.save_as(save_path)
            print(f"Downloaded successfully to: {save_path}", flush=True)

asyncio.run(download_card2())
