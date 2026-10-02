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
    page.wait_for_timeout(4000)

    # Screenshot canvas
    page.screenshot(path="data/tnd_chat_inspect.png")

    # Expand chat if collapsed
    body = page.locator("body").inner_text()
    with open("data/tnd_page_text.txt", "w", encoding="utf-8") as f:
        f.write(body)

    # Check for approval dialog
    approve = page.locator("button:has-text('Approve'), div:has-text('Approve')")
    print(f"Approve buttons: {approve.count()}")
    for i in range(approve.count()):
        print(f"  Approve {i}: {approve.nth(i).inner_text().strip()}")

    browser.close()
