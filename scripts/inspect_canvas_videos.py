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
    
    # Check media cards in center canvas
    # The canvas has 8-10 cards with play_circle icons!
    cards = page.locator("[role='button'], div[class*='asset-card'], div[class*='media-card']")
    print("Cards count:", cards.count())
    
    # Let's inspect video elements or thumbnails in the canvas
    canvas_items = page.locator("div:has(> img), div:has(> video)")
    print("Canvas items with img/video:", canvas_items.count())
    
    # Click on the first video card with play_circle (e.g. top-left item)
    play_icons = page.locator("i:has-text('play_circle'), span:has-text('play_circle'), [class*='play']")
    print("Play circle icons:", play_icons.count())
    if play_icons.count() > 0:
        print("Clicking first play icon to inspect video details...")
        play_icons.first.click(force=True)
        page.wait_for_timeout(3000)
        page.screenshot(path=str(BASE_DIR / "data" / "card_clicked.png"))
        
        # Check download button
        dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('download'), [aria-label*='Export' i]")
        print("Download buttons visible:", dl_btn.count())
        for i in range(dl_btn.count()):
            print(f"DL btn {i}: {dl_btn.nth(i).inner_text()} | aria: {dl_btn.nth(i).get_attribute('aria-label')}")

    ctx.close()
