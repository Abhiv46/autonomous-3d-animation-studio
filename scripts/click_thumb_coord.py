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
    
    # Click session 2
    menu_icon = page.locator("button:has-text('menu'), [aria-label*='Sessions']").first
    menu_icon.click(force=True)
    page.wait_for_timeout(1000)
    s2 = page.locator("text='Playful Pixar Style Story'").first
    s2.click(force=True)
    page.wait_for_timeout(3000)
    
    # In S2, click at the coordinate of the image thumbnail in the chat panel
    # Based on 1920x1080 resolution:
    # Right panel starts at ~1480px, the image is at around X: 1650, Y: 560
    print("Clicking at coordinates (1650, 560)...")
    page.mouse.click(1650, 560)
    page.wait_for_timeout(3000)
    
    page.screenshot(path=str(BASE_DIR / "data" / "after_coord_click.png"))
    print("Screenshot saved to data/after_coord_click.png")

    ctx.close()
