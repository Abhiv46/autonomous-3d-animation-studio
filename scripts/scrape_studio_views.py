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

    print("[*] Navigating to YouTube Studio Content Tab...")
    page.goto("https://studio.youtube.com/channel/UC/videos/short", wait_until="domcontentloaded", timeout=45000)
    time.sleep(4)

    skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
    if skip.count() > 0 and skip.is_visible():
        skip.click()
        time.sleep(3)

    # If short tab didn't load directly, go to content list
    page.goto("https://studio.youtube.com/channel/videos", wait_until="domcontentloaded", timeout=45000)
    time.sleep(4)

    page.screenshot(path="studio_content_list.png")

    rows = page.locator("ytcp-video-row")
    print(f"Total video rows found: {rows.count()}")
    analytics_data = []

    for i in range(min(15, rows.count())):
        row = rows.nth(i)
        try:
            title_el = row.locator("#video-title")
            title = title_el.inner_text().strip() if title_el.count() > 0 else "Unknown"
            
            # Views
            views_el = row.locator(".table-cell-views, [cell-title*='Views' i], td.views")
            views = views_el.inner_text().strip() if views_el.count() > 0 else "0"
            
            # Date
            date_el = row.locator(".table-cell-date, [cell-title*='Date' i]")
            date_str = date_el.inner_text().strip() if date_el.count() > 0 else ""
            
            # Link
            link_el = row.locator("a[href*='/video/']")
            href = link_el.get_attribute("href") if link_el.count() > 0 else ""

            analytics_data.append({
                "index": i + 1,
                "title": title,
                "views": views,
                "date": date_str,
                "edit_href": href
            })
            print(f"{i+1}. [{views} Views] {title[:50]} ({date_str})")
        except Exception as e:
            print(f"Row {i} error: {e}")

    with open("scraped_studio_analytics.json", "w", encoding="utf-8") as f:
        json.dump(analytics_data, f, indent=2, ensure_ascii=False)

    browser.close()
