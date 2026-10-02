import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SAVE_PATH = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips\ep21_highheels_scene3_raw.mp4")

async def download_scene3():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = b.contexts[0].pages[0]
        
        # Click on Scene 3 tile: Girl posing and...
        print("[1] Clicking Scene 3 tile...", flush=True)
        tile = page.locator("[aria-label*='Girl posing and'], [aria-label*='Girl posing']").first
        if await tile.count() == 0:
            tile = page.get_by_text("Girl posing and").first
        await tile.click()
        await page.wait_for_timeout(3000)
        
        # Click more_vert
        print("[2] Opening more menu...", flush=True)
        more_btn = page.locator("button:has-text('more_vert'), button[aria-label*='More'], mat-icon:has-text('more_vert')").first
        await more_btn.click()
        await page.wait_for_timeout(1000)
        
        # Click Download media
        print("[3] Clicking Download media...", flush=True)
        dl_item = page.locator("text='Download media'").first
        
        try:
            async with page.expect_download(timeout=15000) as dl_info:
                await dl_item.click()
            download = await dl_info.value
            await download.save_as(str(SAVE_PATH))
            print(f"[SUCCESS] Downloaded Scene 3 to {SAVE_PATH}", flush=True)
        except Exception as e:
            print("Direct download timed out. Checking 720p submenu...", flush=True)
            sub_opt = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p')").first
            if await sub_opt.count() > 0:
                print("Found 720p submenu, clicking...", flush=True)
                async with page.expect_download(timeout=30000) as dl_info2:
                    await sub_opt.click()
                dl2 = await dl_info2.value
                await dl2.save_as(str(SAVE_PATH))
                print(f"[SUCCESS] Downloaded Scene 3 via submenu to {SAVE_PATH}", flush=True)

asyncio.run(download_scene3())
