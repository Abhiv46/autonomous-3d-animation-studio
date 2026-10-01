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
    url = "https://flow.google.com/u/3/project/a1c6f19b-b046-41f3-9b33-fbc756646163"
    page = ctx.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(6000)
    
    # 1. First, click on "Videos" in the left navigation sidebar
    # Let's inspect all left sidebar items
    sidebar_items = page.locator("mat-sidenav, nav, aside").first.locator("button, a, div[role='button'], div.item, span")
    print("Sidebar items count:", sidebar_items.count())
    for i in range(sidebar_items.count()):
        txt = sidebar_items.nth(i).inner_text().strip()
        if "video" in txt.lower():
            print(f"Clicking left sidebar Videos item: {txt}")
            sidebar_items.nth(i).click(force=True)
            page.wait_for_timeout(3000)
            break
            
    page.screenshot(path=str(BASE_DIR / "data" / "videos_tab_clicked.png"))
    print("Videos tab screenshot saved!")

    ctx.close()
