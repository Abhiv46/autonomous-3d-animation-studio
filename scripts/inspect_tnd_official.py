from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(user_data_dir=BRAVE_DATA, executable_path=BRAVE_EXE, headless=True)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.set_viewport_size({"width": 1600, "height": 1000})

    # Check Slot 0 "The Naughty Duo"
    print("\n=== SLOT 0: The Naughty Duo ===")
    page.goto("https://flow.google.com/u/0/project/1876f0f7-bc42-4764-86c9-35d76cb3a615", wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    page.screenshot(path="data/tnd_slot0_canvas.png")
    cards = page.locator("flow-grid-tile-container, video, div.flow-grid-tile, [aria-label*='video' i]")
    print(f"Slot 0 TND video count: {cards.count()}")

    # Check Slot 2 "The Naughty Duo"
    print("\n=== SLOT 2: The Naughty Duo ===")
    page.goto("https://flow.google.com/u/2/project/0fa549b9-b73f-4dac-8061-365fd0498eb2", wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    page.screenshot(path="data/tnd_slot2_canvas.png")
    cards2 = page.locator("flow-grid-tile-container, video, div.flow-grid-tile, [aria-label*='video' i]")
    print(f"Slot 2 TND video count: {cards2.count()}")

    ctx.close()
