import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

NEW_REEL_URL = "https://www.instagram.com/reel/Dd1sS_kIggc/"
BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def inspect_new_reel():
    print(f"[*] Navigating to new reel: {NEW_REEL_URL}...")
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1400, "height": 950})

        page.goto(NEW_REEL_URL, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)

        # Close any dialog or popup
        page.keyboard.press("Escape")
        close_btn = page.locator("svg[aria-label='Close'], button[aria-label='Close']").first
        if close_btn.count() > 0 and close_btn.is_visible():
            close_btn.click(force=True)

        page.wait_for_timeout(2000)

        # Screenshot the reel frame and metadata
        page.screenshot(path="data/new_reel_Dd1sS_clean.png")

        # Extract text / stats
        body_text = page.locator("body").inner_text()
        with open("data/new_reel_Dd1sS_text.txt", "w", encoding="utf-8") as f:
            f.write(body_text)

        print("[+] Body preview:\n", body_text[:1200])

        # Also get creator profile reels to check exact view count
        # Extract creator username from body or url
        creator = "your_favmochi"
        for line in body_text.splitlines()[:20]:
            if line.strip() and not any(k in line.lower() for k in ["log in", "sign up", "follow", "never miss", "original audio", "ai content"]):
                creator = line.strip()
                break

        print(f"[*] Checking creator profile for exact view count of Dd1sS_kIggc...")
        page.goto(f"https://www.instagram.com/{creator}/reels/", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
        page.screenshot(path="data/new_reel_creator_grid.png")

        # Find link with Dd1sS_kIggc
        target_link = page.locator("a[href*='Dd1sS_kIggc']").first
        if target_link.count() > 0:
            print("Found target reel on grid:", target_link.inner_text().strip().replace("\n", " "))
        else:
            # Check all links
            for a in page.locator("a[href*='/reel/']").all():
                href = a.get_attribute("href") or ""
                txt = a.inner_text().strip().replace("\n", " ")
                print(f"GRID REEL: {href} -> {txt}")

        browser.close()

if __name__ == "__main__":
    inspect_new_reel()
