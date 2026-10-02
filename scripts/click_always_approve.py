from playwright.sync_api import sync_playwright
import time

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

    # Click Always approve button
    always_btn = page.locator("button:has-text('Always approve'), div:has-text('Always approve'), span:has-text('Always approve')").last
    if always_btn.count() > 0:
        print("Clicking 'Always approve'...")
        always_btn.click(force=True)
        page.wait_for_timeout(3000)
    else:
        # Click Approve
        app_btn = page.locator("button:has-text('Approve')").last
        if app_btn.count() > 0:
            print("Clicking 'Approve'...")
            app_btn.click(force=True)
            page.wait_for_timeout(3000)

    page.screenshot(path="data/tnd_after_always_approve.png")

    # Wait for render to complete
    print("[*] Monitoring render to complete...")
    for tick in range(16):
        time.sleep(5)
        stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
        print(f"Tick {tick+1}: Stop button count = {stop_btn.count()}")
        if tick > 3 and stop_btn.count() == 0:
            print("[+] Render finished!")
            break

    browser.close()
