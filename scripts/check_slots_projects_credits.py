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
    for slot, pid in [
        (3, "a1c6f19b-b046-41f3-9b33-fbc756646163"),
        (4, "c30fd23d-5a03-4081-baeb-fad9cbcc6a99"),
        (5, "3782c658-cb27-4a0a-b80b-db721a4ba00e"),
        (6, "11330d30-604f-4829-bb72-9d4f49e64a40"),
        (7, "642a9812-732d-411c-8bbe-380269736158")
    ]:
        url = f"https://flow.google.com/u/{slot}/project/{pid}"
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3500)
        print(f"Slot {slot}: Title = {page.title()}")
        # Check banner for credits
        banners = page.locator("[class*='banner'], [class*='alert']").all()
        for b in banners:
            try:
                t = b.inner_text().strip()
                if "credit" in t.lower():
                    print(f"  Slot {slot} credit alert: {t[:60]}")
            except Exception:
                pass
        page.close()
    ctx.close()
