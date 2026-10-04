import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
VIDEO_ID = "k2JBp96Iqa4"

PL_TITLE = "The Naughty Duo - Kaartik & Kaavya All Episodes 🌈✨"

def add_playlist_via_video():
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

        # Scroll down to Playlists section
        page.evaluate("""() => {
            const el = document.querySelector('ytcp-video-metadata-playlists, [aria-label*=\"playlist\" i], #playlists');
            if (el) el.scrollIntoView();
            else window.scrollBy(0, 500);
        }""")
        page.wait_for_timeout(1000)

        # Look for playlist dropdown
        pl_dropdown = page.locator("ytcp-video-metadata-playlists ytcp-text-dropdown-trigger, [aria-label*='playlist' i] ytcp-text-dropdown-trigger, ytcp-dropdown-trigger").first
        print("[*] Playlist dropdown count:", pl_dropdown.count())
        if pl_dropdown.count() > 0:
            pl_dropdown.click()
            page.wait_for_timeout(1500)
            page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_pl_dropdown_opened.png")
            print("[*] Dropdown opened screenshot saved.")

            # Check if "+ New playlist" button exists in dropdown
            new_pl_btn = page.locator("text='New playlist', ytcp-button:has-text('New playlist')").first
            print("[*] Inside dropdown 'New playlist' count:", new_pl_btn.count())
            if new_pl_btn.count() > 0:
                new_pl_btn.click()
                page.wait_for_timeout(1500)
                # Click 'New playlist' option from submenu if it appeared
                sub_opt = page.locator("text='New playlist'").last
                if sub_opt.count() > 0:
                    sub_opt.click()
                    page.wait_for_timeout(1500)

                # Fill title
                t_input = page.locator("input[placeholder*='Add title' i], [aria-label*='title' i], #title-textarea #textbox").first
                if t_input.count() > 0:
                    t_input.fill(PL_TITLE)
                    page.wait_for_timeout(500)
                    # Click Create / Done
                    btn_create = page.locator("button:has-text('Create'), ytcp-button:has-text('Create')").first
                    if btn_create.count() > 0:
                        btn_create.click()
                        page.wait_for_timeout(2000)

            # Check Done button on playlist picker
            done_btn = page.locator("button:has-text('Done'), ytcp-button:has-text('Done')").first
            if done_btn.count() > 0:
                done_btn.click()
                page.wait_for_timeout(1500)

        # Scroll to top & save
        page.evaluate("""() => {
            window.scrollTo(0, 0);
            const el = document.querySelector('ytcp-animatable#main-content, #scrollable-content, #main');
            if (el) el.scrollTop = 0;
            const saveBtn = document.querySelector('ytcp-button#save-button button, button#save, #save-button button');
            if (saveBtn && !saveBtn.disabled) saveBtn.click();
        }""")
        page.wait_for_timeout(4000)

        proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_playlist_added_to_video.png"
        page.screenshot(path=proof)
        print("Proof saved to:", proof)

        browser.close()

if __name__ == "__main__":
    add_playlist_via_video()
