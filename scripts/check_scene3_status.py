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

    # Ensure we are on canvas
    back_btn = page.locator("button[aria-label*='back' i]").first
    if back_btn.count() > 0 and back_btn.is_visible():
        back_btn.click(force=True)
        page.wait_for_timeout(2000)

    page.screenshot(path="data/tnd_check_scene3_status.png")

    # Read the chat history on the right
    chat_msgs = page.locator(".chat-message, [class*='message'], [class*='conversation']").all_inner_texts()
    print("Chat messages found:", len(chat_msgs))
    for idx, m in enumerate(chat_msgs[-5:]):
        print(f"Msg {idx}: {m[:100]}...")

    # Check tiles
    tiles = page.locator("flow-grid-tile-container, div.flow-grid-tile, [aria-label*='video' i]").all()
    print("Total tiles:", len(tiles))
    for idx, t in enumerate(tiles[:5]):
        print(f"Tile {idx}: {t.get_attribute('aria-label') or t.inner_text()[:40].replace(chr(10), ' ')}")

    browser.close()
