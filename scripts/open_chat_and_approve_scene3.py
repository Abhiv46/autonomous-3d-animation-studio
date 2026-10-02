from playwright.sync_api import sync_playwright

PROJECT_URL = "https://flow.google.com/u/0/project/1876f0f7-bc42-4764-86c9-35d76cb3a615"
BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=BRAVE_DATA,
        executable_path=BRAVE_EXE,
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.set_viewport_size({"width": 1600, "height": 1000})

    page.goto(PROJECT_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(3500)

    # Click the toggle button for chat history / right panel
    # Let's check all header buttons
    header_buttons = page.locator("header button, .header button, [class*='header'] button").all()
    print("Header buttons:", len(header_buttons))
    for idx, b in enumerate(header_buttons):
        print(f"HBtn {idx}: aria='{b.get_attribute('aria-label')}' text='{b.inner_text().strip()}'")

    # Click the button with aria-label or icon that opens the right sidebar
    chat_toggle = page.locator("button[aria-label*='history' i], button[aria-label*='chat' i], button[aria-label*='panel' i], button:has-text('chat')").first
    if chat_toggle.count() > 0:
        print("Clicking chat toggle button...")
        chat_toggle.click()
        page.wait_for_timeout(2000)

    page.screenshot(path="data/tnd_chat_panel_opened.png")

    # Check for Approve button
    approve = page.locator("button:has-text('Approve'), div:has-text('Approve'), span:has-text('Approve')")
    print(f"Approve buttons found: {approve.count()}")
    for idx in range(approve.count()):
        el = approve.nth(idx)
        print(f"Approve {idx}: visible={el.is_visible()} text='{el.inner_text().strip()}'")
        if el.is_visible():
            print(f"Clicking Approve button {idx}...")
            el.click(force=True)
            page.wait_for_timeout(3000)
            page.screenshot(path="data/tnd_scene3_approved.png")
            break

    browser.close()
