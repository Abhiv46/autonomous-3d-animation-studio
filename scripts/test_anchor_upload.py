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
    
    # 1. Click Add media menu
    btn0 = page.locator("[aria-label*='Add media menu' i]").first
    btn0.click()
    time.sleep(1)
    
    # 2. Click Upload with file chooser
    with page.expect_file_chooser() as fc_info:
        page.locator("button:has-text('Upload'), [role='menuitem']:has-text('Upload')").first.click()
        
    fc = fc_info.value
    print(f"Setting file to upload: {TEST_IMG}")
    fc.set_files(TEST_IMG)
    time.sleep(5)
    
    page.screenshot(path="flow_uploaded_test.png")
    print("Uploaded! Checking prompt box or canvas...")
    
    # Inspect what changed in prompt box or media panel
    chips = page.locator("[role='button']:has-text('kaartik'), img, [aria-label*='ingredient' i], [aria-label*='media' i]")
    print(f"Found {chips.count()} related elements.")
    for i in range(min(5, chips.count())):
        el = chips.nth(i)
        print(f"El {i}: tag={el.evaluate('el => el.tagName')} text={el.inner_text().strip()}")
        
    ctx.close()
