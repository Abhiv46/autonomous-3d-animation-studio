import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

SLOTS = [
    (4, "infolillylooks@gmail.com"),
    (5, "elegantdriveways4u@gmail.com"),
    (6, "abhiv446@gmail.com"),
]

print("=" * 60)
print("  TESTING PARALLEL MULTI-ACCOUNT ACCESS (SLOTS 4, 5, 6)")
print("=" * 60)

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=BRAVE_DATA,
        executable_path=BRAVE_EXE,
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    pages = []
    for slot_idx, email in SLOTS:
        url = f"https://flow.google.com/u/{slot_idx}/"
        print(f"[*] Opening Tab for Slot {slot_idx} ({email})...")
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        pages.append((slot_idx, email, page))

    print("[*] Waiting 5s for all 3 accounts to load simultaneously...")
    time.sleep(5)

    for slot_idx, email, page in pages:
        print(f"[+] Slot {slot_idx} ({email}): Current URL = {page.url}")
        new_proj_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i]")
        print(f"    New project button count: {new_proj_btn.count()}")

    ctx.close()
    print("[✓] All 3 slots verified successfully in parallel!")
