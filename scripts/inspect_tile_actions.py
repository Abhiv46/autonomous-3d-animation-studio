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
    
    # 1. Look for custom elements on canvas
    tile_containers = page.locator("flow-grid-tile-container").all()
    print("Tile containers count:", len(tile_containers))
    
    # Hover first tile container
    if tile_containers:
        tc = tile_containers[0]
        tc.hover()
        page.wait_for_timeout(1000)
        page.screenshot(path=str(BASE_DIR / "data" / "tile_hovered.png"))
        
        # Check hotbar buttons
        hotbar_buttons = tc.locator("button, [role='button']").all()
        print("Hotbar buttons on hovered tile:", len(hotbar_buttons))
        for idx, btn in enumerate(hotbar_buttons):
            aria = btn.get_attribute("aria-label") or ""
            txt = btn.inner_text().strip()
            print(f"Hotbar btn {idx}: aria='{aria}', text='{txt}'")
            
        # Click the tile itself (or double click)
        print("Clicking first tile...")
        tc.click(force=True)
        page.wait_for_timeout(2000)
        page.screenshot(path=str(BASE_DIR / "data" / "tile_clicked.png"))
        
        # Check if full view or download option appeared
        dl = page.locator("button[aria-label*='Download' i], [aria-label*='Export' i], button:has-text('download')").all()
        print("Download elements visible:", len(dl))
        for d in dl:
            print(f"Download el: aria='{d.get_attribute('aria-label')}' text='{d.inner_text()}'")

    ctx.close()
