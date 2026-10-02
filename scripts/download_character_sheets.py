import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def download_character_sheets():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            accept_downloads=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        url2 = "https://flow.google.com/u/2/project/0fa549b9-b73f-4dac-8061-365fd0498eb2"
        page.goto(url2, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)

        # Let's inspect the cards at the bottom: Pinki Mom, Kaartik, Kaavya
        # They have labels: "Pinki Mom", "Kaartik", "Kaavya"
        for char_name in ["Kaartik", "Kaavya", "Pinki Mom"]:
            card = page.locator(f"div:has-text('{char_name}'), flow-grid-tile-container:has-text('{char_name}')").last
            if card.count() > 0:
                print(f"[*] Clicking character card: {char_name}")
                card.click(force=True)
                page.wait_for_timeout(2000)
                
                # Check download button
                dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
                if dl_btn.count() > 0 and dl_btn.is_visible():
                    dl_btn.click(force=True)
                    page.wait_for_timeout(1000)
                    orig = page.locator("button:has-text('Original size'), button:has-text('Download original')").first
                    if orig.count() > 0:
                        with page.expect_download(timeout=30000) as dl_info:
                            orig.click(force=True)
                        dl = dl_info.value
                        out_p = rf"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\{char_name}_reference_sheet.png"
                        dl.save_as(out_p)
                        print(f"[✓ SAVED REFERENCE]: {out_p}")
                        page.keyboard.press("Escape")
                        page.wait_for_timeout(1000)

        browser.close()

if __name__ == "__main__":
    download_character_sheets()
