import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SAVE_PATH = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips\ep21_highheels_scene2_raw.mp4")

async def download_media():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = b.contexts[0].pages[0]
        
        # Click 'Download media'
        dl_item = page.locator("text='Download media'").first
        print("Download media item count:", await dl_item.count(), flush=True)
        
        try:
            async with page.expect_download(timeout=15000) as dl_info:
                await dl_item.click()
            download = await dl_info.value
            await download.save_as(str(SAVE_PATH))
            print(f"[SUCCESS] Downloaded to {SAVE_PATH}", flush=True)
        except Exception as e:
            print("Direct download timed out or showed submenu. Checking submenu...", e, flush=True)
            # Check if quality submenu opened (720p, etc.)
            sub_opt = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p')").first
            if await sub_opt.count() > 0:
                print("Found 720p submenu, clicking...", flush=True)
                async with page.expect_download(timeout=30000) as dl_info2:
                    await sub_opt.click()
                dl2 = await dl_info2.value
                await dl2.save_as(str(SAVE_PATH))
                print(f"[SUCCESS] Downloaded via submenu to {SAVE_PATH}", flush=True)

asyncio.run(download_media())
