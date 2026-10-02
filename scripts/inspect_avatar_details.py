from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(user_data_dir=BRAVE_DATA, executable_path=BRAVE_EXE, headless=True)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://flow.google.com/u/0/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    # Click avatar
    avatar = page.locator("a[aria-label*='Google Account' i], button[aria-label*='Google Account' i]").first
    if avatar.count() > 0:
        avatar.click()
        page.wait_for_timeout(2000)
        # Look for popover texts
        popover = page.locator("iframe[name='account'], [role='dialog'], [class*='profile'], [class*='popover']")
        print("Avatar clicked. Frames:", len(page.frames))
        for f in page.frames:
            txt = f.inner_text("body")
            if "credit" in txt.lower() or "storage" in txt.lower() or "plan" in txt.lower():
                print(f"Frame {f.name}: {txt[:200]}")

    # Check Settings (gear icon)
    gear = page.locator("button[aria-label*='Settings' i], button:has-text('settings')").first
    if gear.count() > 0:
        gear.click()
        page.wait_for_timeout(2000)
        dialog = page.locator("[role='dialog']").all_inner_texts()
        print("Settings dialog:", dialog)

    ctx.close()
