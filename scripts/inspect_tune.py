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

    # Click tune icon (settings icon next to send button)
    tune_btn = page.locator("button:has-text('tune'), [aria-label*='settings' i], [aria-label*='tune' i]").last
    if tune_btn.count() > 0:
        print("Clicking tune button...")
        tune_btn.click()
        page.wait_for_timeout(1500)
        page.screenshot(path=str(BASE_DIR / "data" / "tune_settings_open.png"))
        
        # Print menu options
        options = page.locator("[role='menuitem'], mat-option, [role='radiogroup'], button").all_inner_texts()
        print("Tune options:", [o.strip() for o in options if o.strip()][:25])

    ctx.close()
