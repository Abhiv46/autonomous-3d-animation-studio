from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def check():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        for slot in [0, 1, 2]:
            page = browser.new_page()
            page.goto(f"https://flow.google.com/u/{slot}/", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            cards = page.locator("a[href*='/project/']").all()
            print(f"--- Slot {slot} Projects ---")
            for c in cards:
                href = c.get_attribute("href")
                parent_text = c.evaluate("el => el.parentElement ? el.parentElement.innerText : ''").replace("\n", " ")
                print(f"  Href: {href} | Text: {parent_text[:80]}")
            page.close()
        browser.close()

if __name__ == "__main__":
    check()
