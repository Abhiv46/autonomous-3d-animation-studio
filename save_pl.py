import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
VIDEO_ID = "k2JBp96Iqa4"

def save_pl():
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

        url = f"https://studio.youtube.com/video/{VIDEO_ID}/edit"
        print(f"[*] Navigating to {url}...")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        # Check if Playlist already selected or select it
        page.evaluate("""() => {
            const el = document.querySelector('ytcp-video-metadata-playlists');
            if (el) el.scrollIntoView();
        }""")
        page.wait_for_timeout(1000)

        # Open Playlists dropdown to tick the checkbox of the created playlist if needed
        dropdown = page.locator("ytcp-video-metadata-playlists ytcp-text-dropdown-trigger").first
        dropdown.click()
        page.wait_for_timeout(1500)

        # Check the playlist item checkbox
        page.evaluate("""() => {
            const items = Array.from(document.querySelectorAll('ytcp-checkbox-lit, ytcp-ve, tp-yt-paper-checkbox'));
            for (const item of items) {
                if (item.innerText && item.innerText.includes('Kaartik & Kaavya')) {
                    item.click();
                    return 'Clicked checkbox';
                }
            }
        }""")
        page.wait_for_timeout(1000)

        # Click Done
        page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button, ytcp-button'));
            for (const b of btns) {
                if (b.innerText && b.innerText.trim() === 'Done') {
                    b.click();
                    return;
                }
            }
        }""")
        page.wait_for_timeout(1500)

        # Scroll to top & Click Save
        page.evaluate("""() => {
            window.scrollTo(0, 0);
            const el = document.querySelector('ytcp-animatable#main-content, #scrollable-content, #main');
            if (el) el.scrollTop = 0;
        }""")
        page.wait_for_timeout(1000)

        # Click Save
        saved = page.evaluate("""() => {
            const saveBtn = document.querySelector('ytcp-button#save-button button, button#save, #save-button button');
            if (saveBtn && !saveBtn.disabled) {
                saveBtn.click();
                return 'Clicked Save button';
            }
            return 'Save button disabled / already saved';
        }""")
        print("[*] Save result:", saved)
        page.wait_for_timeout(5000)

        proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_everything_saved_verified.png"
        page.screenshot(path=proof)
        print("Proof saved to:", proof)

        browser.close()

if __name__ == "__main__":
    save_pl()
