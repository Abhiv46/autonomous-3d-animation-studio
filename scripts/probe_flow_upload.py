import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

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
        
    print("URL:", page.url)
    
    inputs = page.locator("input[type='file']")
    print("file inputs count:", inputs.count())
    for i in range(inputs.count()):
        inp = inputs.nth(i)
        print(f"Input {i}: accept={inp.get_attribute('accept')} id={inp.get_attribute('id')}")
        
    add_btns = page.locator("[aria-label*='Add media' i], button:has-text('add'), [aria-label*='add' i], [aria-label*='upload' i]")
    print("add buttons count:", add_btns.count())
    for i in range(min(10, add_btns.count())):
        b = add_btns.nth(i)
        print(f"Add Btn {i}: aria='{b.get_attribute('aria-label')}' text='{b.inner_text().strip()}'")
        
    ctx.close()
