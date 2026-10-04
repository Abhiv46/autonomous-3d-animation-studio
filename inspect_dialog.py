import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
VIDEO_ID = "k2JBp96Iqa4"

def inspect_dialog():
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

        # Click Related video
        page.evaluate("""() => {
            const relText = Array.from(document.querySelectorAll('*')).find(el => el.textContent && el.textContent.trim() === 'Related video');
            if (relText) {
                let p = relText.parentElement;
                while (p && !p.querySelector('button, [role=\"button\"], ytcp-icon-button')) {
                    p = p.parentElement;
                }
                const btn = p ? p.querySelector('button, [role=\"button\"], ytcp-icon-button') : null;
                if (btn) btn.click();
            }
        }""")

        # Wait for "Choose specific video" modal
        print("[*] Waiting for modal...")
        page.wait_for_selector("text='Choose specific video'", timeout=15000)
        page.wait_for_timeout(2000)

        # Inspect cards inside modal
        cards = page.evaluate("""() => {
            const modal = document.querySelector('ytcp-video-pick-dialog, ytcp-dialog, [role=\"dialog\"]');
            if (!modal) return 'No dialog found';
            const items = modal.querySelectorAll('*');
            const found = [];
            for (const item of items) {
                if (item.children.length === 0 && item.innerText && item.innerText.trim().length > 3) {
                    found.push({tag: item.tagName, text: item.innerText.trim()});
                }
            }
            return found.slice(0, 20);
        }""")
        print("[*] Found elements in modal:", cards)

        # Click directly using coordinate of one of the items or search input
        search_input = page.locator("input[placeholder*='Search' i], [aria-label*='Search' i]").first
        if search_input.count() > 0:
            print("[+] Found search input! Typing 'Red Button'...")
            search_input.fill("Red Button")
            page.wait_for_timeout(2000)
            page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_related_search.png")
            
            # Click first result
            res = page.evaluate("""() => {
                const modal = document.querySelector('ytcp-video-pick-dialog, ytcp-dialog, [role=\"dialog\"]');
                const row = modal ? modal.querySelector('ytcp-entity-card, ytcp-video-row, [role=\"option\"], .style-scope.ytcp-video-pick-dialog') : null;
                if (row) {
                    row.click();
                    return 'Clicked search result';
                }
                return 'No result row';
            }""")
            print("[*] Result click:", res)
            page.wait_for_timeout(2000)

        # Save
        page.evaluate("""() => {
            window.scrollTo(0, 0);
            const el = document.querySelector('ytcp-animatable#main-content, #scrollable-content, #main');
            if (el) el.scrollTop = 0;
            const saveBtn = document.querySelector('ytcp-button#save-button button, button#save, #save-button button');
            if (saveBtn && !saveBtn.disabled) saveBtn.click();
        }""")
        page.wait_for_timeout(4000)

        page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_related_after_search.png")
        browser.close()

if __name__ == "__main__":
    inspect_dialog()
