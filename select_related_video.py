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

def select_related_video():
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

        page.wait_for_selector("#description-textarea #textbox", timeout=30000)

        # Open Related video modal
        print("[*] Opening Related video picker...")
        page.evaluate("""() => {
            const relText = Array.from(document.querySelectorAll('*')).find(el => el.textContent && el.textContent.trim() === 'Related video');
            if (relText) {
                let p = relText.parentElement;
                while (p && !p.querySelector('button, [role=\"button\"], ytcp-icon-button')) {
                    p = p.parentElement;
                }
                const btn = p ? p.querySelector('button, [role=\"button\"], ytcp-icon-button') : null;
                if (btn) btn.click();
                else relText.click();
            }
        }""")
        page.wait_for_timeout(2000)

        # Click the target related video: 'Red Button Ko Mat Dabana!'
        target_video = page.locator("text='Red Button Ko Mat Dabana!'").first
        if target_video.count() > 0:
            print("[+] Found 'Red Button Ko Mat Dabana!' in modal, clicking...")
            target_video.click()
            page.wait_for_timeout(2000)
        else:
            print("[-] Could not find target by text, clicking first card...")
            first_card = page.locator("ytcp-video-pick-item, ytcp-entity-card, [role='listbox'] > *").first
            first_card.click()
            page.wait_for_timeout(2000)

        # Scroll to top
        page.evaluate("""() => {
            window.scrollTo(0, 0);
            const el = document.querySelector('ytcp-animatable#main-content, #scrollable-content, #main');
            if (el) el.scrollTop = 0;
        }""")
        page.wait_for_timeout(1000)

        # Click Save button
        save_btn = page.locator("ytcp-button#save-button button, button#save, #save-button button, ytcp-button#save-button").first
        if save_btn.count() > 0:
            is_disabled = save_btn.get_attribute("disabled")
            aria_disabled = save_btn.get_attribute("aria-disabled")
            print(f"[*] Save button status: disabled={is_disabled}, aria-disabled={aria_disabled}")
            if is_disabled is None and aria_disabled != "true":
                print("[+] Clicking Save...")
                save_btn.click(force=True)
                page.wait_for_timeout(4000)
                print("[✓] Save clicked successfully!")
            else:
                print("[*] Save button already disabled.")

        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_related_picked_success.png"
        page.screenshot(path=proof_path)
        print(f"[✓] Proof screenshot saved: {proof_path}")

        browser.close()

if __name__ == "__main__":
    select_related_video()
