import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

PL_TITLE = "The Naughty Duo - Kaartik & Kaavya All Episodes 🌈✨"
PL_DESC  = "Watch all funny, magical, and cute 3D cartoon adventures of Kaartik & Kaavya in non-stop playlist order! Subscribe to @TheNaughtyDuoOfficial."

def create_playlist():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        url = "https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/content/playlists"
        print(f"[*] Navigating to {url}...")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        # Click New playlist button
        new_btn = page.locator("button:has-text('New playlist'), ytcp-button:has-text('New playlist')").first
        if new_btn.count() > 0:
            print("[+] Clicking New playlist...")
            new_btn.click()
            page.wait_for_timeout(2000)

        # Fill Title
        title_input = page.locator("#title-textarea #textbox, [aria-label*='title' i], [aria-label*='Add title' i], input[placeholder*='Add title' i]").first
        if title_input.count() > 0:
            print("[+] Filling Playlist Title...")
            title_input.click()
            title_input.fill(PL_TITLE)
            page.wait_for_timeout(500)

        # Fill Description
        desc_input = page.locator("#description-textarea #textbox, [aria-label*='description' i], [aria-label*='Add description' i]").first
        if desc_input.count() > 0:
            print("[+] Filling Playlist Description...")
            desc_input.click()
            desc_input.fill(PL_DESC)
            page.wait_for_timeout(500)

        # Click Create button INSIDE the modal
        print("[*] Clicking Create button inside dialog...")
        create_btn = page.locator("[role='dialog'], ytcp-playlist-creation-dialog").locator("button, ytcp-button").filter(has_text="Create").first
        if create_btn.count() > 0:
            create_btn.click(force=True)
            print("[+] Clicked dialog Create button via Playwright locator!")
        else:
            print("[*] Fallback: coordinate click on Create button at (1005, 810)...")
            page.mouse.click(1005, 810)

        page.wait_for_timeout(5000)

        proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_playlist_created_verified.png"
        page.screenshot(path=proof)
        print("Playlist creation screenshot saved to:", proof)

        browser.close()

if __name__ == "__main__":
    create_playlist()
