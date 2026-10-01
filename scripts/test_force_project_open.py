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
    
    # Remove any overlays
    try:
        page.evaluate("() => document.querySelectorAll('.cdk-overlay-container, .cdk-overlay-backdrop').forEach(el => el.remove())")
    except Exception:
        pass
    
    # Click tile with force=True
    tile = page.get_by_text("The Naughty Duo").first
    print("[*] Clicking 'The Naughty Duo' tile with force=True...")
    tile.click(force=True)
    page.wait_for_timeout(6000)
    print("[+] SUCCESS! Project Opened URL:", page.url)
    
    # Check editor
    editor = page.locator("[contenteditable='true'], div.ProseMirror")
    print("[+] Prompt Editor Count:", editor.count())
    
    # Check characters on canvas
    body = page.locator("body").inner_text()
    for char in ["Pinki", "Kaartik", "Kaavya"]:
        print(f"    - Character '{char}' on canvas:", char in body)
        
    ctx.close()
