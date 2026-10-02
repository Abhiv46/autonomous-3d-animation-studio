import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

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

    page.goto("https://studio.youtube.com", wait_until="domcontentloaded", timeout=45000)
    time.sleep(3)

    skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
    if skip.count() > 0 and skip.is_visible():
        skip.click()
        time.sleep(3)

    # Click Content icon on left sidebar
    content_link = page.locator("a#menu-item-1, a[test-id='content'], #menu-paper-icon-item-1").first
    if content_link.count() > 0:
        content_link.click()
    else:
        page.locator("tp-yt-paper-icon-item:has-text('Content'), [aria-label*='Content' i]").first.click()
    time.sleep(4)

    # Click 'Shorts' subtab
    shorts_tab = page.locator("tp-yt-paper-tab:has-text('Shorts'), div:has-text('Shorts')").first
    if shorts_tab.count() > 0:
        shorts_tab.click()
        time.sleep(3)

    page.screenshot(path="studio_shorts_tab.png")

    rows = page.locator("ytcp-video-row")
    print(f"Total video rows on Shorts tab: {rows.count()}")
    scraped = []
    for i in range(min(20, rows.count())):
        row = rows.nth(i)
        t = row.locator("#video-title").inner_text().strip() if row.locator("#video-title").count() > 0 else ""
        v = row.locator(".table-cell-views").inner_text().strip() if row.locator(".table-cell-views").count() > 0 else "0"
        d = row.locator(".table-cell-date").inner_text().strip() if row.locator(".table-cell-date").count() > 0 else ""
        print(f"{i+1}. [{v} views] {t[:45]} | {d}")
        scraped.append({"title": t, "views": v, "date": d})

    with open("studio_shorts_views.json", "w", encoding="utf-8") as f:
        json.dump(scraped, f, indent=2, ensure_ascii=False)

    browser.close()
