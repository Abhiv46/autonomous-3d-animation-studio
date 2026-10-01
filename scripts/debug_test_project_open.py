import sys
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

brave_exe = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
brave_data = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=brave_data,
        executable_path=brave_exe,
        headless=True
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://flow.google.com/u/0/", timeout=25000)
    page.wait_for_timeout(4000)
    
    # Check current email on /u/0/
    print("[1] Home Page URL:", page.url)
    user_btn = page.locator("[aria-label='Account details'], .header-user-button")
    if user_btn.count() > 0:
        user_btn.first.click()
        page.wait_for_timeout(1500)
        body = page.locator("body").inner_text()
        print("[2] Account Details Text:")
        for line in body.split("\n"):
            if "@" in line or "credit" in line.lower():
                print("    -", line)
        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)
    
    # Open 'The Naughty Duo' project
    tile = page.get_by_text("The Naughty Duo").first
    print("[3] Clicking 'The Naughty Duo' project tile...")
    tile.click()
    page.wait_for_timeout(6000)
    print("[4] Opened Project URL:", page.url)
    
    # Check editor
    editor = page.locator("[contenteditable='true'], div.ProseMirror")
    print("[5] Prompt Editor Count:", editor.count())
    
    # Check characters on canvas
    body_canvas = page.locator("body").inner_text()
    for char in ["Pinki", "Kaartik", "Kaavya"]:
        print(f"    - Character '{char}' found on canvas:", char in body_canvas)
        
    ctx.close()
