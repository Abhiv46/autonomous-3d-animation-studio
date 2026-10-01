import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent

brave_exe = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
brave_data = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=brave_data,
        executable_path=brave_exe,
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = ctx.new_page()
    page.goto("https://flow.google.com/u/0/", wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(5000)
    
    shot_path = str(BASE_DIR / "data" / "flow_dashboard_home.png")
    page.screenshot(path=shot_path)
    print("Dashboard home screenshot:", shot_path)
    print("Page URL:", page.url)
    
    # List all links
    links = page.locator("a").all()
    print("Found links:", len(links))
    for l in links:
        try:
            href = l.get_attribute("href")
            text = l.inner_text()
            if "project" in str(href) or "Naughty" in text:
                print(f"Project link: href={href}, text={text}")
        except Exception:
            pass

    ctx.close()
