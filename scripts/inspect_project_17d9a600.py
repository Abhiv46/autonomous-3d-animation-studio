from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(user_data_dir=BRAVE_DATA, executable_path=BRAVE_EXE, headless=True)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.set_viewport_size({"width": 1600, "height": 1000})
    page.goto("https://flow.google.com/u/0/project/17d9a600-d978-4f15-a549-e6a4b271e629", wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    page.screenshot(path="data/project_17d9a600_canvas.png")
    cards = page.locator("flow-grid-tile-container, video, div.flow-grid-tile")
    print("Cards count:", cards.count())
    for i in range(cards.count()):
        c = cards.nth(i)
        print(f"Card {i}:", c.get_attribute("aria-label") or c.inner_text()[:40].replace("\n", " "))
    ctx.close()
