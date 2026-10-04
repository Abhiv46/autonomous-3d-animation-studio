import asyncio
import sys
from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

VIDEO_ID = "k2JBp96Iqa4"

VIRAL_DESCRIPTION = (
    "Kaartik aur Kaavya pahunch gaye ek jadui Rainbow World me jahan se saare rang gayab ho gaye! 🌈✨\n"
    "Lekin kya Kaavya aur Kaartik milkar Laal Seb, Neeli Titli, Peela Suraj aur Saare Colors wapas laa payenge? 🍎🦋☀️\n\n"
    "Dekhiye unka sabse pyara aur mazedaar Magic Color Adventure! 🥰🎉\n\n"
    "❓ Sawaal: Aapka sabse favourite color kaunsa hai? Comment me batayein! ❤️💙💛\n\n"
    "🔔 Aise hi mazedaar aur cute 3D family cartoon stories ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! ✨\n\n"
    "#TheNaughtyDuo #shorts #viral #funny #colorsong #rainbow #3danimation #hindicartoon #kidsanimation #cartoons #trending #ytshorts #learningcolors #funnycartoon #family"
)

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

async def update_seo():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = b.contexts[0]
        
        target_page = None
        for pg in context.pages:
            if "studio.youtube.com" in pg.url and VIDEO_ID in pg.url:
                target_page = pg
                break
        
        if not target_page:
            for pg in context.pages:
                if "studio.youtube.com" in pg.url:
                    target_page = pg
                    break

        if not target_page:
            target_page = await context.new_page()

        edit_url = f"https://studio.youtube.com/video/{VIDEO_ID}/edit"
        if edit_url not in target_page.url:
            print(f"[*] Navigating to {edit_url}...", flush=True)
            await target_page.goto(edit_url, wait_until="networkidle", timeout=45000)
            await target_page.wait_for_timeout(3000)
        else:
            print(f"[*] Already on {edit_url}!", flush=True)

        # Scroll to top
        await target_page.evaluate("""() => {
            window.scrollTo(0, 0);
            const main = document.querySelector('ytcp-animatable#main-content, #scrollable-content, #main');
            if (main) main.scrollTop = 0;
        }""")
        await target_page.wait_for_timeout(1000)

        # 1. Update Description
        print("[*] Finding description textarea...", flush=True)
        desc_box = target_page.locator("#description-textarea #textbox, [aria-label*='Tell viewers' i], #textbox[aria-label*='description' i]").first
        if await desc_box.count() > 0:
            print("[+] Clicking description box...", flush=True)
            await desc_box.click()
            await target_page.wait_for_timeout(300)
            await target_page.keyboard.press("Control+A")
            await target_page.keyboard.press("Backspace")
            await target_page.wait_for_timeout(300)
            await desc_box.fill(VIRAL_DESCRIPTION)
            print("[+] Filled description successfully!", flush=True)
            # Dismiss any autocomplete hashtag menu
            await target_page.wait_for_timeout(500)
            await target_page.keyboard.press("Escape")
            await target_page.keyboard.press("Escape")
            await target_page.wait_for_timeout(500)
        else:
            print("[-] Description box not found!", flush=True)

        # 2. Scroll down and open 'Show more' for tags
        print("[*] Checking 'Show more' button...", flush=True)
        show_more = target_page.locator("#toggle-button, button:has-text('Show more')").first
        if await show_more.count() > 0 and await show_more.is_visible():
            text = await show_more.inner_text()
            print(f"[*] 'Show more' text: {text}", flush=True)
            if "more" in text.lower():
                await show_more.click()
                await target_page.wait_for_timeout(1500)

        # 3. Check and add Tags
        print("[*] Checking tags input...", flush=True)
        tags_input = target_page.locator("#tags-container input, input[aria-label='Tags'], #tags-container #text-input").first
        if await tags_input.count() > 0:
            print("[+] Tags input found! Checking existing tags...", flush=True)
            existing_chips = await target_page.locator("#tags-container ytcp-chip").all_text_contents()
            print(f"[*] Current tags count: {len(existing_chips)}", flush=True)
            if len(existing_chips) < 5:
                print("[*] Adding viral tags...", flush=True)
                await tags_input.click()
                for tag in VIRAL_TAGS:
                    await target_page.keyboard.type(tag)
                    await target_page.keyboard.press("Enter")
                    await target_page.wait_for_timeout(150)
                print("[+] All viral tags added!", flush=True)
            else:
                print(f"[+] Tags already present ({len(existing_chips)} tags):", existing_chips[:5], flush=True)
        else:
            print("[-] Tags input not visible or not found!", flush=True)

        # 4. Scroll to top to ensure Save button is clear
        await target_page.evaluate("""() => {
            window.scrollTo(0, 0);
            const main = document.querySelector('ytcp-animatable#main-content, #scrollable-content, #main');
            if (main) main.scrollTop = 0;
        }""")
        await target_page.wait_for_timeout(1000)
        await target_page.keyboard.press("Escape")
        await target_page.wait_for_timeout(500)

        # 5. Click Save Button
        save_btn = target_page.locator("ytcp-button#save-button button, button#save, #save-button button").first
        if await save_btn.count() > 0:
            is_disabled = await save_btn.get_attribute("disabled")
            aria_disabled = await save_btn.get_attribute("aria-disabled")
            print(f"[*] Save button status: disabled={is_disabled}, aria-disabled={aria_disabled}", flush=True)
            if is_disabled is None and aria_disabled != "true":
                await save_btn.click(force=True)
                print("[+] Clicked SAVE button!", flush=True)
                await target_page.wait_for_timeout(4000)
            else:
                print("[*] Save button is disabled (data already saved).", flush=True)
        else:
            print("[-] Save button not located via selector.", flush=True)

        # Take confirmation screenshot
        out_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_color_tags_desc_saved_proof.png"
        await target_page.screenshot(path=out_path)
        print(f"[SUCCESS] Final proof screenshot saved to {out_path}!", flush=True)

if __name__ == "__main__":
    asyncio.run(update_seo())
