import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
VIDEO_ID = "k2JBp96Iqa4"

def click_card_exact():
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

        # Open Related video modal
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
        page.wait_for_timeout(2500)

        # Click Card 2 at (590, 340)
        print("[*] Clicking Card 2 at (590, 340)...")
        page.mouse.click(590, 340)
        page.wait_for_timeout(2000)

        # Scroll to top & save
        page.evaluate("""() => {
            window.scrollTo(0, 0);
            const el = document.querySelector('ytcp-animatable#main-content, #scrollable-content, #main');
            if (el) el.scrollTop = 0;
            const saveBtn = document.querySelector('ytcp-button#save-button button, button#save, #save-button button');
            if (saveBtn && !saveBtn.disabled) saveBtn.click();
        }""")
        page.wait_for_timeout(4000)

        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_related_coord_590.png"
        page.screenshot(path=proof_path)
        print("Proof screenshot saved successfully to:", proof_path)

        browser.close()

if __name__ == "__main__":
    click_card_exact()
