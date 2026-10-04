import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
VIDEO_ID = "k2JBp96Iqa4"

def setup_related_video():
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
        page.wait_for_timeout(4000)

        # Look for Related video section
        related_btn = page.locator("text='Related video'").first
        print("[*] Checking Related video locator count:", related_btn.count())

        # Click the edit button for Related video
        rel_clicked = page.evaluate("""() => {
            const relSection = Array.from(document.querySelectorAll('*')).find(el => el.textContent && el.textContent.trim() === 'Related video');
            if (relSection) {
                // Find nearest parent or container
                let parent = relSection.parentElement;
                while (parent && !parent.querySelector('button, [role=\"button\"], ytcp-icon-button')) {
                    parent = parent.parentElement;
                }
                if (parent) {
                    const btn = parent.querySelector('button, [role=\"button\"], ytcp-icon-button, #edit-button');
                    if (btn) {
                        btn.click();
                        return 'Clicked Related Video button: ' + btn.tagName;
                    }
                }
                relSection.click();
                return 'Clicked relSection directly';
            }
            return 'Related video not found';
        }""")
        print("[*] Related video click result:", rel_clicked)
        page.wait_for_timeout(3000)

        # Check if dialog opened
        page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_related_dialog.png")
        print("[*] Screenshot saved to yt_related_dialog.png")

        # Select first video from dialog if present
        video_item = page.locator("ytcp-video-row, ytcp-entity-card, [role='row'], #video-list ytcp-video-pick-item, ytcp-video-list-cell-video").first
        print("[*] Dialog video row count:", video_item.count())
        
        selected_vid = page.evaluate("""() => {
            const rows = document.querySelectorAll('ytcp-video-row, [role=\"row\"], ytcp-video-pick-item, #video-title');
            for (const r of rows) {
                if (r.innerText && r.innerText.trim().length > 3 && !r.innerText.includes('Rainbow Duniya')) {
                    r.click();
                    return 'Selected: ' + r.innerText.trim().slice(0, 50);
                }
            }
            return 'No suitable other video row found';
        }""")
        print("[*] Selection result:", selected_vid)
        page.wait_for_timeout(2000)

        # Scroll to top & click Save
        page.evaluate("""() => {
            window.scrollTo(0, 0);
            const el = document.querySelector('ytcp-animatable#main-content, #scrollable-content, #main');
            if (el) el.scrollTop = 0;
        }""")
        page.wait_for_timeout(1000)

        save_res = page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button, ytcp-button'));
            for (const b of btns) {
                if (b.innerText && b.innerText.trim() === 'Save') {
                    const isDisabled = b.getAttribute('disabled') !== null || b.getAttribute('aria-disabled') === 'true';
                    if (!isDisabled) {
                        b.click();
                        return 'Clicked Save button!';
                    }
                    return 'Save button disabled / already saved';
                }
            }
            return 'Save button not found';
        }""")
        print("[*] Save result:", save_res)
        page.wait_for_timeout(4000)

        page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_related_saved_proof.png")
        print("[*] Final proof saved to yt_related_saved_proof.png")

        browser.close()

if __name__ == "__main__":
    setup_related_video()
