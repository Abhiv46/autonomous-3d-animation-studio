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
    print("=" * 60)
    print(f"  UPDATING SEO, TAGS & DESCRIPTION FOR: https://youtube.com/shorts/{VIDEO_ID}")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        url = f"https://studio.youtube.com/video/{VIDEO_ID}/edit"
        print(f"[*] Navigating to {url}...")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)

        # Skip dialog if present
        skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
        if skip.count() > 0 and skip.is_visible():
            skip.click()
            page.wait_for_timeout(2000)

        # 1. Title verification / update
        title_box = page.locator("#textbox[aria-label*='title' i], [aria-label*='Add a title' i]").first
        if title_box.count() > 0:
            current_title = title_box.inner_text()
            print(f"[*] Current title: {current_title}")
            if "Magical Rainbow" not in current_title:
                title_box.click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                title_box.fill(VIRAL_TITLE)
                print("[✓] Title set!")
                page.wait_for_timeout(500)

        # 2. Description update
        desc_box = page.locator("#description-textarea #textbox, [aria-label*='Tell viewers' i]").first
        if desc_box.count() > 0:
            print("[*] Setting Description...")
            desc_box.click()
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            desc_box.fill(VIRAL_DESCRIPTION)
            print("[✓] Full Description filled!")
            page.wait_for_timeout(500)
            # Dismiss hashtag dropdown
            page.keyboard.press("Escape")
            page.wait_for_timeout(300)
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)

        # 3. Show More for Tags
        show_more = page.locator("#toggle-button, button:has-text('Show more')").first
        if show_more.count() > 0 and show_more.is_visible():
            txt = show_more.inner_text()
            if "more" in txt.lower():
                print("[*] Clicking 'Show more' for tags...")
                show_more.click()
                page.wait_for_timeout(1500)

        tags_input = page.locator("#tags-container input, input[aria-label='Tags']").first
        if tags_input.count() > 0:
            existing_tags = page.locator("#tags-container ytcp-chip").all_text_contents()
            print(f"[*] Existing tags count: {len(existing_tags)}")
            if len(existing_tags) < 5:
                print("[*] Injecting Viral High-Search-Volume Tags...")
                tags_input.click()
                for t in VIRAL_TAGS:
                    page.keyboard.type(t)
                    page.keyboard.press("Enter")
                    time.sleep(0.15)
                print("[✓] 15 Viral Tags injected!")
            else:
                print(f"[✓] Tags already present: {len(existing_tags)} tags found.")

        # 4. Scroll to top to ensure Save button is clear
        page.evaluate("""() => {
            window.scrollTo(0, 0);
            const main = document.querySelector('ytcp-animatable#main-content, #scrollable-content, #main');
            if (main) main.scrollTop = 0;
        }""")
        page.wait_for_timeout(1000)
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)

        # 5. Save Changes
        top_save = page.locator("ytcp-button#save, ytcp-button:has-text('Save'), #save-button button").first
        if top_save.count() > 0:
            is_enabled = top_save.is_enabled()
            print(f"[*] Top Save enabled: {is_enabled}")
            if is_enabled:
                top_save.click()
                page.wait_for_timeout(5000)
                print("[🚀 SUPREME SEO SAVED SUCCESSFULLY!]")
            else:
                print("[*] Save button was already disabled / up to date.")
        else:
            print("[-] Top save button not found by locator, trying generic selector...")
            page.locator("button#save").click(timeout=3000)
            page.wait_for_timeout(5000)

        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_seo_verified_final.png"
        page.screenshot(path=proof_path)
        print(f"[✓] Screenshot proof saved to {proof_path}")

        browser.close()

if __name__ == "__main__":
    main()
