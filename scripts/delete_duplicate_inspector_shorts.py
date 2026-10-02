import sys
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def delete_duplicates():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
        if skip.count() > 0 and skip.is_visible():
            skip.click()
            page.wait_for_timeout(3000)

        # Find all rows matching 'Inspector Kaartik Ne Pakda Mummy Ko!'
        # Rows 2, 3, 4, 5 (all 4 are duplicates with bad graphics)
        rows = page.locator("ytcp-video-row:has-text('Inspector Kaartik Ne Pakda Mummy Ko!')")
        count = rows.count()
        print(f"[*] Found {count} Inspector Kaartik rows to delete.")

        # Delete each one cleanly
        for i in range(count):
            print(f"[*] Deleting duplicate #{i+1}...")
            target_row = page.locator("ytcp-video-row:has-text('Inspector Kaartik Ne Pakda Mummy Ko!')").first
            if target_row.count() == 0:
                break
            
            # Hover over row to reveal action buttons
            target_row.hover()
            page.wait_for_timeout(1000)

            # Click Options menu (three dots)
            dots = target_row.locator("ytcp-icon-button#options-menu-button, ytcp-icon-button[aria-label*='Options' i]").first
            if dots.count() > 0:
                dots.click(force=True)
                page.wait_for_timeout(1000)

                # Click Delete forever
                del_btn = page.locator("text='Delete forever'").first
                if del_btn.count() > 0:
                    del_btn.click(force=True)
                    page.wait_for_timeout(1500)

                    # Check confirmation checkbox
                    chk = page.locator("tp-yt-paper-checkbox#confirm-checkbox, tp-yt-paper-checkbox").first
                    if chk.count() > 0:
                        chk.click(force=True)
                        page.wait_for_timeout(1000)

                    # Click confirm Delete forever button
                    confirm_del = page.locator("ytcp-button#confirm-button, button:has-text('Delete forever')").first
                    if confirm_del.count() > 0:
                        confirm_del.click(force=True)
                        print(f"[✓ Deleted duplicate #{i+1}]")
                        page.wait_for_timeout(4000)

        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\yt_studio_after_cleanup.png")
        browser.close()

if __name__ == "__main__":
    delete_duplicates()
