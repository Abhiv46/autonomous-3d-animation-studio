import os
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

VIRAL_TITLE = "Kaartik & Kaavya Ki Magical Rainbow Duniya! 🌈✨ Colors Magic Quest! 🥰🎨 #TheNaughtyDuo #shorts"

VIRAL_DESCRIPTION = """Kaartik aur Kaavya pahunch gaye ek jadui Rainbow World me jahan se saare rang gayab ho gaye! 🌈✨
Lekin kya Kaavya aur Kaartik milkar Laal Seb, Neeli Titli, Peela Suraj aur Saare Colors wapas laa payenge? 🍎🦋☀️

Dekhiye unka sabse pyara aur mazedaar Magic Color Adventure! 🥰🎉

❓ Sawaal: Aapka sabse favourite color kaunsa hai? Comment me batayein! ❤️💙💛

🔔 Aise hi mazedaar aur cute 3D family cartoon stories ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! ✨

#TheNaughtyDuo #shorts #viral #funny #colorsong #rainbow #3danimation #hindicartoon #kidsanimation #cartoons #trending #ytshorts #learningcolors #funnycartoon #family"""

VIRAL_TAGS = [
    "The Naughty Duo",
    "TheNaughtyDuo",
    "Kaartik and Kaavya",
    "learn colors hindi",
    "color song",
    "rainbow cartoon",
    "3d animation hindi",
    "hindi cartoon funny",
    "kids animation",
    "nursery rhyme hindi",
    "cartoon for toddlers",
    "relatable comedy",
    "shorts",
    "viral shorts",
    "trending shorts"
]

def main():
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

        # Handle 'SKIP TO YOUTUBE STUDIO'
        skip = page.locator("text='SKIP TO YOUTUBE STUDIO', a:has-text('SKIP TO YOUTUBE STUDIO'), [role='button']:has-text('SKIP')").first
        if skip.count() > 0 and skip.is_visible():
            print("[*] Found 'SKIP TO YOUTUBE STUDIO', clicking...")
            skip.click()
            page.wait_for_timeout(4000)

        # Wait for description box or title box to be visible
        print("[*] Waiting for studio editor elements...")
        page.wait_for_selector("#description-textarea #textbox, [aria-label*='Tell viewers' i], #textbox[aria-label*='description' i]", timeout=30000)
        page.wait_for_timeout(2000)

        # 1. Update Description
        desc_box = page.locator("#description-textarea #textbox, [aria-label*='Tell viewers' i], #textbox[aria-label*='description' i]").first
        if desc_box.count() > 0:
            print("[+] Found Description box! Filling description...")
            desc_box.click()
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            desc_box.fill(VIRAL_DESCRIPTION)
            print("[✓] Description successfully filled!")
            page.wait_for_timeout(1000)
            page.keyboard.press("Escape")
            page.wait_for_timeout(300)
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)

        # 2. Scroll down & open 'Show more' for tags
        print("[*] Expanding 'Show more'...")
        page.evaluate("""() => {
            const el = Array.from(document.querySelectorAll('*')).find(e => e.textContent && e.textContent.trim() === 'Show more');
            if (el) el.click();
            const btn = document.querySelector('#toggle-button');
            if (btn) btn.click();
        }""")
        page.wait_for_timeout(2000)

        # 3. Handle Tags
        print("[*] Checking tags...")
        tags_input = page.locator("#tags-container input, input[aria-label='Tags'], #tags-container #text-input").first
        if tags_input.count() > 0:
            existing_tags = page.locator("#tags-container ytcp-chip").all_text_contents()
            print(f"[*] Existing tags count: {len(existing_tags)}")
            if len(existing_tags) < 5:
                print("[*] Typing tags into input...")
                tags_input.click()
                for tag in VIRAL_TAGS:
                    page.keyboard.type(tag)
                    page.keyboard.press("Enter")
                    time.sleep(0.15)
                print("[✓] Injected 15 viral tags!")
            else:
                print(f"[✓] Tags already configured ({len(existing_tags)} tags).")
        else:
            print("[-] Tags input not found!")

        # 4. Scroll to top to ensure Save button is visible & click Save
        page.evaluate("""() => {
            window.scrollTo(0, 0);
            const main = document.querySelector('ytcp-animatable#main-content, #scrollable-content, #main');
            if (main) main.scrollTop = 0;
        }""")
        page.wait_for_timeout(1000)
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)

        save_btn = page.locator("ytcp-button#save-button button, button#save, #save-button button, ytcp-button#save-button").first
        if save_btn.count() > 0:
            is_disabled = save_btn.get_attribute("disabled")
            aria_disabled = save_btn.get_attribute("aria-disabled")
            print(f"[*] Save button status: disabled={is_disabled}, aria-disabled={aria_disabled}")
            if is_disabled is None and aria_disabled != "true":
                print("[*] Clicking SAVE button...")
                save_btn.click(force=True)
                page.wait_for_timeout(4000)
                print("[🚀 SUCCESS: Saved changes to YouTube!]")
            else:
                print("[*] Save button is disabled (already up to date).")

        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_seo_verified_final.png"
        page.screenshot(path=proof_path)
        print(f"[✓] Final screenshot saved to {proof_path}")

        browser.close()

if __name__ == "__main__":
    main()
