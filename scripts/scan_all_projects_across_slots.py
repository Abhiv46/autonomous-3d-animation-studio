from playwright.sync_api import sync_playwright
import re

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

SLOTS = [0, 1, 2, 3, 4, 5, 6, 7]

def scan_all_slots_projects():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        for slot in SLOTS:
            print(f"\n=================== SCANNING SLOT {slot} PROJECTS ===================")
            page.goto(f"https://flow.google.com/u/{slot}/", wait_until="domcontentloaded")
            page.wait_for_timeout(3500)

            # Get project cards / links
            links = page.locator("a[href*='/project/']").all()
            print(f"Slot {slot} has {len(links)} project links:")
            seen = set()
            for l in links:
                href = l.get_attribute("href") or ""
                txt = l.inner_text().replace("\n", " ").strip()
                if href and href not in seen:
                    seen.add(href)
                    print(f"  -> [{txt}] : {href}")

        ctx.close()

if __name__ == "__main__":
    scan_all_slots_projects()
