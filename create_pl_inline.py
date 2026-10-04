import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
VIDEO_ID = "k2JBp96Iqa4"

PL_TITLE = "The Naughty Duo - Kaartik & Kaavya All Episodes 🌈✨"
PL_DESC  = "Watch all funny, magical, and cute 3D cartoon adventures of Kaartik & Kaavya in non-stop playlist order! Subscribe to @TheNaughtyDuoOfficial."

def create_pl_inline():
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
        print("[*] 'Create playlist' button count:", create_pl_btn.count())
        create_pl_btn.click()
        page.wait_for_timeout(1000)

        # Click 'New playlist' in popup menu
        new_opt = page.get_by_text("New playlist").first
        print("[*] 'New playlist' option count:", new_opt.count())
        new_opt.click()
        page.wait_for_timeout(2000)

        # Fill Title
        title_box = page.locator("textarea[placeholder*='Add title' i], input[placeholder*='Add title' i], #title-textarea #textbox, [aria-label*='Add title' i], #textbox").first
        print("[*] Title box count:", title_box.count())
        if title_box.count() > 0:
            title_box.fill(PL_TITLE)
            page.wait_for_timeout(500)

        # Fill Description
        desc_box = page.locator("textarea[placeholder*='Add description' i], input[placeholder*='Add description' i], #description-textarea #textbox, [aria-label*='Add description' i]").first
        if desc_box.count() > 0:
            desc_box.fill(PL_DESC)
            page.wait_for_timeout(500)

        # Click Create button strictly inside the modal dialog
        dialog = page.locator("ytcp-playlist-creation-dialog, [role='dialog'], tp-yt-paper-dialog").last
        create_confirm = dialog.locator("button:has-text('Create'), ytcp-button:has-text('Create'), #create-button").first
        print("[*] Scoped create button count:", create_confirm.count())
        if create_confirm.count() > 0:
            create_confirm.click(force=True)
            print("[+] Clicked scoped Create button!")
            page.wait_for_timeout(3500)

        # Click Done button on dropdown
        done_btn = page.get_by_text("Done").first
        if done_btn.count() > 0 and done_btn.is_visible():
            done_btn.click()
            page.wait_for_timeout(1500)

        # Scroll to top & Save
        page.evaluate("""() => {
            window.scrollTo(0, 0);
            const el = document.querySelector('ytcp-animatable#main-content, #scrollable-content, #main');
            if (el) el.scrollTop = 0;
            const saveBtn = document.querySelector('ytcp-button#save-button button, button#save, #save-button button');
            if (saveBtn && !saveBtn.disabled) saveBtn.click();
        }""")
        page.wait_for_timeout(4000)

        proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_playlist_live_confirmed.png"
        page.screenshot(path=proof)
        print("Proof saved to:", proof)

        browser.close()

if __name__ == "__main__":
    create_pl_inline()
