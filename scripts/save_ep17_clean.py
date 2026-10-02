import os
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

VIDEO_ID = "HBmHJVsL0Ok"

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

    url = f"https://studio.youtube.com/video/{VIDEO_ID}/edit"
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    time.sleep(4)

    skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
    if skip.count() > 0 and skip.is_visible():
        skip.click()
        time.sleep(3)

    # Show more
    show_more = page.locator("#toggle-button, button:has-text('Show more')").first
    if show_more.count() > 0 and show_more.is_visible():
        show_more.click()
        time.sleep(1)

    # Look at delete icons in tags
    icons = page.locator("[aria-label*='delete' i], [aria-label*='remove' i], ytcp-chip ytcp-icon-button, ytcp-chip iron-icon")
    print(f"Delete icon count: {icons.count()}")
    for _ in range(min(5, icons.count())):
        curr_icons = page.locator("ytcp-chip iron-icon[icon*='cancel'], ytcp-chip [aria-label*='delete' i], ytcp-chip ytcp-icon-button")
        if curr_icons.count() > 0:
            curr_icons.last.click(force=True)
            time.sleep(0.3)

    # Save
    save_btn = page.locator("ytcp-button#save, ytcp-button:has-text('Save'), #save-button, button:has-text('Save')").first
    print("Save button enabled:", save_btn.is_enabled())
    if save_btn.is_enabled():
        save_btn.click()
        time.sleep(4)
        print("[🎉] TAG TRIMMED & EPISODE 17 SAVED!")

    page.screenshot(path="studio_ep17_final_saved.png")
    browser.close()
