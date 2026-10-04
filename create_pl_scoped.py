import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
VIDEO_ID = "k2JBp96Iqa4"

PL_TITLE = "The Naughty Duo - Kaartik & Kaavya All Episodes 🌈✨"

def create_pl_scoped():
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

        # Scope strictly inside the modal dialog
        dialog = page.locator("ytcp-playlist-creation-dialog, [role='dialog'], tp-yt-paper-dialog").last
        
        # Type into title box inside dialog
        title_box = dialog.locator("#title-textarea #textbox, [aria-label*='title' i], textarea, input").first
        print("[*] Scoped Title box count:", title_box.count())
        if title_box.count() > 0:
            title_box.click(force=True)
            page.wait_for_timeout(300)
            page.keyboard.type(PL_TITLE, delay=20)
            page.wait_for_timeout(1000)

        # Click Create button at (1115, 854)
        print("[*] Clicking Create button at (1115, 854)...")
        page.mouse.click(1115, 854)
        page.wait_for_timeout(3000)

        # Click Done button on dropdown
        print("[*] Clicking Done button...")
        done_clicked = page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button, ytcp-button'));
            for (const b of btns) {
                if (b.innerText && b.innerText.trim() === 'Done') {
                    b.click();
                    return 'Clicked Done';
                }
            }
            return 'Done not found';
        }""")
        print("[*] Done result:", done_clicked)
        page.wait_for_timeout(2000)

        # Scroll to top & Save
        page.evaluate("""() => {
            window.scrollTo(0, 0);
            const el = document.querySelector('ytcp-animatable#main-content, #scrollable-content, #main');
            if (el) el.scrollTop = 0;
            const saveBtn = document.querySelector('ytcp-button#save-button button, button#save, #save-button button');
            if (saveBtn && !saveBtn.disabled) saveBtn.click();
        }""")
        page.wait_for_timeout(4000)

        proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_playlist_scoped_success.png"
        page.screenshot(path=proof)
        print("Proof saved to:", proof)

        browser.close()

if __name__ == "__main__":
    create_pl_scoped()
