from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(user_data_dir=BRAVE_DATA, executable_path=BRAVE_EXE, headless=True)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://www.instagram.com/your_favmochi/reels/", wait_until="domcontentloaded")
    page.wait_for_timeout(4000)

    # Hover over the reel cards to extract play counts
    articles = page.locator("a[href*='/reel/']").all()
    for a in articles:
        href = a.get_attribute("href")
        txt = a.inner_text().strip().replace("\n", " ")
        print(f"HREF: {href} | TEXT: {txt}")

    ctx.close()
