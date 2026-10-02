import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=BRAVE_DATA,
        executable_path=BRAVE_EXE,
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto("https://studio.youtube.com/video/2wePkYa9lqw/edit", wait_until="domcontentloaded", timeout=45000)
    time.sleep(6)
    page.screenshot(path="inspect_studio_edit.png")
    
    tbs = page.locator("#textbox")
    print("Textbox count:", tbs.count())
    for i in range(tbs.count()):
        el = tbs.nth(i)
        aria = el.get_attribute("aria-label") or ""
        print(f"Textbox {i}: aria='{aria}'")
        
    save_btns = page.locator("button:has-text('Save'), ytcp-button:has-text('Save'), #save-button")
    print("Save btn count:", save_btns.count())
    for i in range(save_btns.count()):
        sb = save_btns.nth(i)
        txt = sb.inner_text().strip()
        bid = sb.get_attribute("id") or ""
        print(f"Save btn {i}: id='{bid}' text='{txt}'")
        
    browser.close()
