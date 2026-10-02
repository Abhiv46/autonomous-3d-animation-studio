from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(user_data_dir=BRAVE_DATA, executable_path=BRAVE_EXE, headless=True)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://flow.google.com/u/5/project/3782c658-cb27-4a0a-b80b-db721a4ba00e", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    for el in page.locator("text=/.*credit.*/i").all():
        txt = el.inner_text().strip().replace("\n", " ")
        if len(txt) < 120:
            print("FOUND:", txt)
    ctx.close()
