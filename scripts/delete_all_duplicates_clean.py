import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def delete_all_inspector_duplicates():
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

        while True:
            page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", wait_until="domcontentloaded")
            page.wait_for_timeout(4000)

            skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
            if skip.count() > 0 and skip.is_visible():
                skip.click()
                page.wait_for_timeout(3000)

            target_row = page.locator("ytcp-video-row:has-text('Inspector Kaartik Ne Pakda Mummy Ko!')").first
            if target_row.count() == 0:
                print("[*] No more Inspector Kaartik rows found! Cleanup complete.")
                break

            print("[*] Found Inspector Kaartik row. Hovering and clicking menu...")
            target_row.hover()
            page.wait_for_timeout(1000)

            dots = target_row.locator("ytcp-icon-button#options-menu-button, ytcp-icon-button[aria-label*='Options' i]").first
            if dots.count() > 0:
                dots.click(force=True)
                page.wait_for_timeout(1500)

                del_btn = page.locator("text='Delete forever'").first
                if del_btn.count() > 0:
                    del_btn.click(force=True)
                    page.wait_for_timeout(2000)

                    chk = page.locator("tp-yt-paper-checkbox#confirm-checkbox, tp-yt-paper-checkbox").first
                    if chk.count() > 0:
                        chk.click(force=True)
                        page.wait_for_timeout(1000)

                    confirm_del = page.locator("ytcp-button#confirm-button, button:has-text('Delete forever')").first
                    if confirm_del.count() > 0:
                        confirm_del.click(force=True)
                        print("[✓ Deleted one duplicate row]")
                        page.wait_for_timeout(5000)
            else:
                print("[-] Could not find three dots menu.")
                break

        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\yt_studio_clean_state.png")
        browser.close()

if __name__ == "__main__":
    delete_all_inspector_duplicates()
