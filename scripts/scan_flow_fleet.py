import time
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def scan():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        for slot in range(8):
            page = browser.new_page()
            try:
                page.goto(f"https://flow.google.com/u/{slot}/", wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(3000)
                
                # Check email
                acc_label = "Unknown"
                account_elements = page.locator("[aria-label*='@gmail.com' i], [aria-label*='Google Account' i]")
                if account_elements.count() > 0:
                    acc_label = account_elements.first.get_attribute("aria-label") or "Found"
                
                # Check banner
                banners = page.locator("[role='banner'], .banner, div:has-text('credit')")
                credit_status = "CLEAN (CREDITS LIKELY AVAILABLE)"
                for i in range(banners.count()):
                    txt = banners.nth(i).inner_text()
                    if "out of Google Flow credits" in txt:
                        credit_status = "EXHAUSTED (Out of credits)"
                        break
                    elif "running low" in txt:
                        credit_status = "LOW (Some credits remaining)"
                        break
                    elif "reached your credit limit" in txt:
                        credit_status = "EXHAUSTED (Limit reached)"
                        break

                print(f"Slot {slot}: URL={page.url} | Account={acc_label} | Status={credit_status}")
            except Exception as e:
                print(f"Slot {slot}: Error - {e}")
            finally:
                page.close()
        browser.close()

if __name__ == "__main__":
    scan()
