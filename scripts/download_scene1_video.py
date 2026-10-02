import time
from pathlib import Path
from playwright.sync_api import sync_playwright

DOWNLOAD_PATH = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips\ep21_highheels_scene1_raw.mp4")
DOWNLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Find the first tile (top-leftmost tile: Girl walking in gi...)
    tiles = page.locator("flow-grid-tile-container, [role='gridcell'], .flow-grid-tile").all()
    print("Found tiles:", len(tiles))

    if tiles:
        print("Clicking Tile 0 (Scene 1 Video)...")
        tiles[0].click(force=True)
        page.wait_for_timeout(3000)

        # Look for Download button
        dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
        if dl_btn.count() == 0:
            dl_btn = page.locator("button:has(mat-icon:has-text('download'))").first

        print("Download button count:", dl_btn.count())
        if dl_btn.count() > 0:
            dl_btn.click(force=True)
            page.wait_for_timeout(1500)

            # Look for 720p or Original size in dropdown menu
            opt = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size'), button:has-text('1080p')").first
            print("Download option count:", opt.count())

            if opt.count() > 0:
                print("Triggering download...")
                with page.expect_download(timeout=60000) as dl_info:
                    opt.click(force=True)
                dl = dl_info.value
                dl.save_as(str(DOWNLOAD_PATH))
                print(f"[✓] Downloaded successfully to: {DOWNLOAD_PATH}")
            else:
                print("Attempting direct download if no quality menu...")
                with page.expect_download(timeout=60000) as dl_info:
                    dl_btn.click(force=True)
                dl = dl_info.value
                dl.save_as(str(DOWNLOAD_PATH))
                print(f"[✓] Downloaded directly: {DOWNLOAD_PATH}")

        # Click Done or back
        done_btn = page.locator("button:has-text('Done'), button[aria-label*='back' i]").first
        if done_btn.count() > 0 and done_btn.is_visible():
            done_btn.click(force=True)
            page.wait_for_timeout(1500)
