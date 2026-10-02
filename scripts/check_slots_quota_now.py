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
    for slot in [7, 5, 6, 4, 0]:
        page = ctx.new_page()
        page.goto(f"https://flow.google.com/u/{slot}/", wait_until="domcontentloaded", timeout=35000)
        time.sleep(3)
        body = page.locator("body").inner_text()
        quota_hit = any(w in body.lower() for w in ["reached your generation quota", "credit limit", "limit for now", "try again later"])
        print(f"Slot {slot}: Quota Limit Hit = {quota_hit}")
        page.close()
    ctx.close()
