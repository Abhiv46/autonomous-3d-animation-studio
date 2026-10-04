import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
VIDEO_ID = "k2JBp96Iqa4"

def inspect_title_input():
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

        # Inspect all elements inside ytcp-playlist-creation-dialog
        elements = page.evaluate("""() => {
            const dlg = document.querySelector('ytcp-playlist-creation-dialog');
            if (!dlg) return 'no dlg';
            const inputs = dlg.querySelectorAll('textarea, input, [contenteditable], #textbox');
            return Array.from(inputs).map(i => {
                const r = i.getBoundingClientRect();
                return {
                    tag: i.tagName,
                    id: i.id,
                    ariaLabel: i.getAttribute('aria-label'),
                    rect: {x: r.x, y: r.y, w: r.width, h: r.height}
                };
            });
        }""")
        print("[*] Modal inputs:", elements)

        browser.close()

if __name__ == "__main__":
    inspect_title_input()
