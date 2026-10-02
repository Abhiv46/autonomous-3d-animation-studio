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
    
    # 1. Click bottom '+' button
    plus_btn = page.locator("[aria-label*='Add ingredients' i]").last
    plus_btn.click()
    time.sleep(1)
    
    # 2. Click Upload media with file chooser
    with page.expect_file_chooser() as fc_info:
        page.locator("button:has-text('Upload media'), div:has-text('Upload media')").last.click()
        
    fc = fc_info.value
    print(f"Setting file to upload: {TEST_IMG}")
    fc.set_files(TEST_IMG)
    time.sleep(4)
    
    # 3. Click "Add to prompt"
    add_btn = page.locator("button:has-text('Add to prompt'), [role='button']:has-text('Add to prompt')").first
    print("Add to prompt button count:", add_btn.count())
    if add_btn.count() > 0:
        add_btn.click()
        time.sleep(2)
        print("Clicked Add to prompt!")
        
    page.screenshot(path="prompt_with_anchor.png")
    
    # Check editor
    editor = page.locator("[contenteditable='true'], div.ProseMirror").first
    print("Editor innerHTML after Add to prompt:", editor.evaluate("el => el.innerHTML"))
    
    ctx.close()
