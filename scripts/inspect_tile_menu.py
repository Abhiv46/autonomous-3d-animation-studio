import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=BRAVE_DATA,
        executable_path=BRAVE_EXE,
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = ctx.new_page()
    page.goto("https://flow.google.com/u/4/project/5997b7be-97fa-431b-bd68-4428567b3a51", wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(4000)

    # Click the first generated tile
    tiles = page.locator("img, [role='img'], mat-card").all()
    print("Found image elements:", len(tiles))
    
    # Click the second tile (Kaartik + Freeze Mummy)
    if len(tiles) >= 2:
        tiles[1].click()
        page.wait_for_timeout(2000)
        page.screenshot(path=str(BASE_DIR / "data" / "tile_action_menu.png"))
        
        # Check buttons available
        btns = page.locator("button, [role='button'], [role='menuitem']").all()
        btn_texts = [b.inner_text().strip() for b in btns if b.inner_text().strip()]
        print("Action buttons:", btn_texts[:20])

    ctx.close()
