from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(user_data_dir=BRAVE_DATA, executable_path=BRAVE_EXE, headless=True)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://flow.google.com/u/0/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    btn = page.locator("[aria-label='Account details'], .header-user-button").first
    if btn.count() > 0:
        print("Found Account details button, clicking...")
        btn.click()
        page.wait_for_timeout(2000)
        page.screenshot(path="data/account_details_modal.png")
        # Print modal text
        modal = page.locator("[role='dialog'], [class*='dialog'], [class*='overlay'], [class*='popover'], mat-dialog-container").first
        if modal.count() > 0:
            print("MODAL TEXT:\n", modal.inner_text())
        else:
            print("BODY TEXT AFTER CLICK:\n", page.locator("body").inner_text()[-1000:])
    ctx.close()
