from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(user_data_dir=BRAVE_DATA, executable_path=BRAVE_EXE, headless=True)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://flow.google.com/u/2/project/0fa549b9-b73f-4dac-8061-365fd0498eb2", wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    page.screenshot(path="data/slot2_tnd_canvas.png")
    tiles = page.locator("flow-grid-tile-container, div.flow-grid-tile, [aria-label*='video' i]").all()
    print("Slot 2 tiles count:", len(tiles))
    for idx, t in enumerate(tiles[:6]):
        print(f"Tile {idx}:", t.get_attribute("aria-label") or t.inner_text()[:40].replace("\n", " "))
    ctx.close()
