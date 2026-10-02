import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
TEST_IMG = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\benchmark_mROirKAfmE4_kaartik.jpg"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=BRAVE_DATA,
        executable_path=BRAVE_EXE,
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = ctx.new_page()
    page.goto("https://flow.google.com/u/7/", wait_until="domcontentloaded", timeout=45000)
    time.sleep(3)
    
    new_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i]").first
    if new_btn.count() > 0:
        new_btn.click()
        time.sleep(4)
        
    print("Project URL:", page.url)
    
    # Try Add media menu (Btn 0)
    btn0 = page.locator("[aria-label*='Add media menu' i]").first
    if btn0.count() > 0:
        btn0.click()
        time.sleep(2)
        print("Clicked Add media menu. Looking for menu items...")
        menu_items = page.locator("[role='menuitem'], button")
        for i in range(menu_items.count()):
            txt = menu_items.nth(i).inner_text().strip()
            if any(w in txt.lower() for w in ["upload", "image", "asset", "media", "file"]):
                print(f"Menu item {i}: {txt}")
                
    # Also check Add ingredients (Btn 1)
    btn1 = page.locator("[aria-label*='Add ingredients' i]").first
    if btn1.count() > 0:
        print("\nBtn 1 exists: aria=", btn1.get_attribute("aria-label"))
        
    ctx.close()
