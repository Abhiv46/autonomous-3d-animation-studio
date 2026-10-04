import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def check_and_create_playlist():
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
        page.wait_for_timeout(4000)

        page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_playlists_page.png")
        print("[*] Playlists screenshot saved.")

        # Check existing playlists
        existing = page.evaluate("""() => {
            const rows = Array.from(document.querySelectorAll('ytcp-playlist-row, [role=\"row\"], a[href*=\"playlist\"]'));
            return rows.map(r => r.innerText.trim()).filter(t => t.length > 2);
        }""")
        print("[*] Existing playlists:", existing)

        # Check if 'New playlist' button exists
        new_btn = page.locator("button:has-text('New playlist'), ytcp-button:has-text('New playlist')").first
        print("[*] New playlist button count:", new_btn.count())
        if new_btn.count() > 0:
            new_btn.click()
            page.wait_for_timeout(2000)
            page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_new_playlist_modal.png")

        browser.close()

if __name__ == "__main__":
    check_and_create_playlist()
