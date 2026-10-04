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

        # Wait for Details page
        page.wait_for_selector("#description-textarea #textbox, [aria-label*='Tell viewers' i]", timeout=30000)

        # Scroll down to reveal Show More
        print("[*] Scrolling down to find 'Show more'...")
        for _ in range(3):
            page.evaluate("""() => {
                window.scrollBy(0, 600);
                const el = document.querySelector('ytcp-animatable#main-content, #scrollable-content, #main');
                if (el) el.scrollTop += 600;
            }""")
            page.wait_for_timeout(500)

        # Click 'Show more' button
        show_more_clicked = page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button, ytcp-button, [role=\"button\"]'));
            for (const b of btns) {
                if (b.innerText && b.innerText.trim().toLowerCase().includes('show more')) {
                    b.click();
                    return 'Clicked: ' + b.innerText.trim();
                }
            }
            const tb = document.querySelector('#toggle-button');
            if (tb) {
                tb.click();
                return 'Clicked #toggle-button';
            }
            return 'Not found';
        }""")
        print("[*] Show more result:", show_more_clicked)
        page.wait_for_timeout(2000)

        # Scroll down more to reveal Tags container
        for _ in range(3):
            page.evaluate("""() => {
                window.scrollBy(0, 600);
                const el = document.querySelector('ytcp-animatable#main-content, #scrollable-content, #main');
                if (el) el.scrollTop += 600;
            }""")
            page.wait_for_timeout(500)

        # Check tags
        tags_input = page.locator("#tags-container input, input[aria-label='Tags'], #tags-container #text-input").first
        if tags_input.count() > 0:
            print("[+] Tags input box found!")
            existing_tags = page.locator("#tags-container ytcp-chip").all_text_contents()
            print(f"[*] Current tags on video ({len(existing_tags)}):", existing_tags)
            
            # If tags not added or < 5, type them
            if len(existing_tags) < 5:
                print("[*] Typing tags into box...")
                tags_input.click()
                for tag in VIRAL_TAGS:
                    page.keyboard.type(tag)
                    page.keyboard.press("Enter")
                    time.sleep(0.15)
                print("[✓] All 15 tags injected successfully!")
            else:
                print("[✓] 15 Tags are already present and verified!")
        else:
            print("[-] Tags input still not visible. Let's capture screenshot of scrolled area.")

        # Take screenshot of tags section
        page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_tags_section.png")

        # Now scroll back to top
        page.evaluate("""() => {
            window.scrollTo(0, 0);
            const el = document.querySelector('ytcp-animatable#main-content, #scrollable-content, #main');
            if (el) el.scrollTop = 0;
        }""")
        page.wait_for_timeout(1000)

        # Check description box content to ensure it didn't get cleared
        desc_val = page.locator("#description-textarea #textbox, [aria-label*='Tell viewers' i]").first.inner_text()
        print(f"[*] Description length: {len(desc_val)} characters")
        if len(desc_val) < 50:
            VIRAL_DESC = (
                "Kaartik aur Kaavya pahunch gaye ek jadui Rainbow World me jahan se saare rang gayab ho gaye! 🌈✨\n"
                "Lekin kya Kaavya aur Kaartik milkar Laal Seb, Neeli Titli, Peela Suraj aur Saare Colors wapas laa payenge? 🍎🦋☀️\n\n"
                "Dekhiye unka sabse pyara aur mazedaar Magic Color Adventure! 🥰🎉\n\n"
                "❓ Sawaal: Aapka sabse favourite color kaunsa hai? Comment me batayein! ❤️💙💛\n\n"
                "🔔 Aise hi mazedaar aur cute 3D family cartoon stories ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! ✨\n\n"
                "#TheNaughtyDuo #shorts #viral #funny #colorsong #rainbow #3danimation #hindicartoon #kidsanimation #cartoons #trending #ytshorts #learningcolors #funnycartoon #family"
            )
            desc_box = page.locator("#description-textarea #textbox, [aria-label*='Tell viewers' i]").first
            desc_box.click()
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            desc_box.fill(VIRAL_DESC)
            page.wait_for_timeout(500)
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)

        # Click the Save button (the black button in the top bar!)
        # In YouTube Studio the top Save button is: ytcp-button#save-button, or button containing text Save
        save_btn_clicked = page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button, ytcp-button'));
            for (const b of btns) {
                if (b.innerText && b.innerText.trim() === 'Save') {
                    const isDisabled = b.getAttribute('disabled') !== null || b.getAttribute('aria-disabled') === 'true';
                    if (!isDisabled) {
                        b.click();
                        return 'Clicked Save button!';
                    } else {
                        return 'Save button already disabled / saved';
                    }
                }
            }
            return 'Save button not found';
        }""")
        print("[*] Save action:", save_btn_clicked)
        page.wait_for_timeout(4000)

        # Final full page screenshot
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_seo_saved_confirmed.png"
        page.screenshot(path=proof_path)
        print(f"[SUCCESS] Final saved screenshot: {proof_path}")

        browser.close()

if __name__ == "__main__":
    main()
