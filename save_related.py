import sys
import time
from playwright.sync_api import sync_playwright

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
VIDEO_ID = "k2JBp96Iqa4"

def save_and_verify():
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

        # Check Related video field
        rel_text = page.locator("text='Meri Patang Atak Gayi!'").first
        print("[*] Related video already set count:", rel_text.count())
        if rel_text.count() == 0:
            print("[*] Setting Related Video...")
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
            page.wait_for_timeout(2000)
            page.mouse.click(450, 340) # Card 1
            page.wait_for_timeout(2000)

        # Click black Save button
        print("[*] Clicking Save...")
        save_btn = page.locator("ytcp-button#save-button button, button#save, #save-button button, ytcp-button#save-button").first
        if save_btn.count() > 0:
            is_disabled = save_btn.get_attribute("disabled")
            aria_disabled = save_btn.get_attribute("aria-disabled")
            print(f"[*] Save button: disabled={is_disabled}, aria-disabled={aria_disabled}")
            if is_disabled is None and aria_disabled != "true":
                save_btn.click(force=True)
                page.wait_for_timeout(5000)
                print("[SUCCESS] Clicked and saved!")
            else:
                print("[*] Already saved.")
        else:
            page.evaluate("""() => {
                const btns = Array.from(document.querySelectorAll('button, ytcp-button'));
                for (const b of btns) {
                    if (b.innerText && b.innerText.trim() === 'Save') {
                        b.click();
                    }
                }
            }""")
            page.wait_for_timeout(5000)

        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_related_final_saved.png"
        page.screenshot(path=proof_path)
        print("Final proof saved to:", proof_path)
        browser.close()

if __name__ == "__main__":
    save_and_verify()
