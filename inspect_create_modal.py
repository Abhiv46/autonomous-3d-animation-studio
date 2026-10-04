import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
VIDEO_ID = "k2JBp96Iqa4"

def inspect_create_modal():
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
            const el = document.querySelector('ytcp-video-metadata-playlists, [aria-label*=\"playlist\" i], #playlists');
            if (el) el.scrollIntoView();
            else window.scrollBy(0, 500);
        }""")
        page.wait_for_timeout(1000)

        # Open Playlists dropdown
        pl_dropdown = page.locator("ytcp-video-metadata-playlists ytcp-text-dropdown-trigger, [aria-label*='playlist' i] ytcp-text-dropdown-trigger, ytcp-dropdown-trigger").first
        pl_dropdown.click()
        page.wait_for_timeout(1500)

        # Click 'Create playlist' button at bottom left of dropdown
        create_pl_btn = page.get_by_text("Create playlist").first
        create_pl_btn.click()
        page.wait_for_timeout(1000)

        # Click 'New playlist' in popup menu
        new_opt = page.get_by_text("New playlist").first
        new_opt.click()
        page.wait_for_timeout(2000)

        # Inspect all elements with "Create"
        info = page.evaluate("""() => {
            const all = Array.from(document.querySelectorAll('*'));
            const res = [];
            for (const el of all) {
                if (el.innerText && el.innerText.trim() === 'Create') {
                    const rect = el.getBoundingClientRect();
                    res.push({
                        tag: el.tagName,
                        id: el.id,
                        className: el.className,
                        rect: {x: rect.x, y: rect.y, w: rect.width, h: rect.height},
                        visible: rect.width > 0 && rect.height > 0
                    });
                }
            }
            return res;
        }""")
        print("[*] All 'Create' elements:", info)

        browser.close()

if __name__ == "__main__":
    inspect_create_modal()
