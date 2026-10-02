import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # In Agent settings:
    # 1. Select 9:16 for Image generation
    print("Configuring Image generation default to 9:16...")
    img_916 = page.locator("text='9:16'").first
    if img_916.count() > 0:
        img_916.click(force=True)
        page.wait_for_timeout(500)

    # 2. Select 9:16 for Video generation
    print("Configuring Video generation default to 9:16...")
    vid_916 = page.locator("text='9:16'").last
    if vid_916.count() > 0:
        vid_916.click(force=True)
        page.wait_for_timeout(500)

    # 3. Click Save button
    print("Clicking Save button...")
    save_btn = page.locator("button:has-text('Save')").first
    if save_btn.count() > 0:
        save_btn.click(force=True)
        page.wait_for_timeout(2000)

    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\settings_saved_916.png")
    print("Settings successfully saved to 9:16 vertical!")
