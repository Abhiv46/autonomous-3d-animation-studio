import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
VIDEO_ID = "k2JBp96Iqa4"

PL_TITLE = "The Naughty Duo - Kaartik & Kaavya All Episodes 🌈✨"
PL_DESC  = "Watch all funny, magical, and cute 3D cartoon adventures of Kaartik & Kaavya in non-stop playlist order! Subscribe to @TheNaughtyDuoOfficial."

def run():
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

        # Scroll to Playlists
        page.evaluate("""() => {
            const el = document.querySelector('ytcp-video-metadata-playlists');
            if (el) el.scrollIntoView();
        }""")
        page.wait_for_timeout(1000)

        # Open Playlists dropdown
        page.locator("ytcp-video-metadata-playlists ytcp-text-dropdown-trigger").first.click()
        page.wait_for_timeout(1500)
        page.get_by_text("Create playlist").first.click()
        page.wait_for_timeout(1000)
        page.get_by_text("New playlist").first.click()
        page.wait_for_timeout(2000)

        # Click Title Box at (886, 357)
        print("[*] Clicking Title box at (886, 357)...")
        page.mouse.click(886, 357)
        page.wait_for_timeout(300)
        page.keyboard.type(PL_TITLE, delay=15)
        page.wait_for_timeout(500)

        # Click Description Box at (886, 496)
        print("[*] Clicking Description box at (886, 496)...")
        page.mouse.click(886, 496)
        page.wait_for_timeout(300)
        page.keyboard.type(PL_DESC, delay=15)
        page.wait_for_timeout(1000)

        # Click Create button at (1115, 855)
        print("[*] Clicking Create button at (1115, 855)...")
        page.mouse.click(1115, 855)
        page.wait_for_timeout(4000)

        # Click Done button on dropdown
        print("[*] Clicking Done...")
        page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button, ytcp-button'));
            for (const b of btns) {
                if (b.innerText && b.innerText.trim() === 'Done') {
                    b.click();
                    return;
                }
            }
        }""")
        page.wait_for_timeout(2000)

        # Scroll to top & Save
        print("[*] Saving video metadata...")
        page.evaluate("""() => {
            window.scrollTo(0, 0);
            const el = document.querySelector('ytcp-animatable#main-content, #scrollable-content, #main');
            if (el) el.scrollTop = 0;
            const saveBtn = document.querySelector('ytcp-button#save-button button, button#save, #save-button button');
            if (saveBtn && !saveBtn.disabled) saveBtn.click();
        }""")
        page.wait_for_timeout(4000)

        proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_playlist_100pct_done.png"
        page.screenshot(path=proof)
        print("Success proof saved to:", proof)

        browser.close()

if __name__ == "__main__":
    run()
