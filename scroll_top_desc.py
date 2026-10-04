import asyncio
from playwright.async_api import async_playwright

VID_ID = "k2JBp96Iqa4"

YT_DESC = (
    "Kaartik aur Kaavya pahunch gaye ek jadui Rainbow World me jahan se saare rang gayab ho gaye! 🌈😱\n"
    "Lekin kya Kaavya aur Kaartik milkar Laal Seb, Neeli Titli, Peela Suraj aur Saare Colors wapas laa payenge? 🍎🦋☀️🌱\n\n"
    "Dekhiye unka sabse pyara aur mazedaar Magic Color Adventure! 🥰✨\n\n"
    "💬 Sawaal: Aapka sabse favourite color kaunsa hai? Comment me batayein! 👇❤️💙💛💚\n\n"
    "🔔 Aise hi mazedaar aur cute 3D family cartoon stories ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! ✨\n\n"
    "#TheNaughtyDuo #shorts #viral #funny #colorsong #rainbow #3danimation #hindicartoon #kidsanimation #cartoons #trending #ytshorts #learningcolors #funnycartoon #family"
)

async def run():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = [pg for pg in b.contexts[0].pages if "studio.youtube.com" in pg.url][0]
        
        # Scroll to top of page and main scrollable container
        await page.evaluate("""() => {
            window.scrollTo(0, 0);
            const scrollable = document.querySelector('ytcp-animatable#main-content, #scrollable-content, #main');
            if (scrollable) scrollable.scrollTop = 0;
        }""")
        await page.wait_for_timeout(1000)

        # Click the description area
        desc_box = page.locator("#textbox[aria-label*='description' i], #description-textarea #textbox, [aria-label*='Tell viewers' i]").first
        if await desc_box.count() > 0:
            print("[+] Found description box!", flush=True)
            await desc_box.click()
            await page.wait_for_timeout(300)
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await desc_box.fill(YT_DESC)
            print("[+] Filled description!", flush=True)
            await page.wait_for_timeout(1000)
            
            # Click Save button
            save_btn = page.locator("button#save, ytcp-button#save-button").first
            if await save_btn.count() > 0 and await save_btn.is_enabled():
                await save_btn.click()
                print("[+] Clicked Save button!", flush=True)
                await page.wait_for_timeout(4000)
        else:
            print("Description box not found directly, checking placeholder...")
            placeholder = page.locator("text='Tell viewers about your video'").first
            if await placeholder.count() > 0:
                await placeholder.click()
                await page.keyboard.type(YT_DESC)
                print("[+] Typed into placeholder!", flush=True)
                await page.wait_for_timeout(1000)
                save_btn = page.locator("button#save, ytcp-button#save-button").first
                if await save_btn.count() > 0 and await save_btn.is_enabled():
                    await save_btn.click()
                    print("[+] Clicked Save button!", flush=True)
                    await page.wait_for_timeout(4000)

        proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_color_desc_saved_top.png"
        await page.screenshot(path=proof)
        print(f"[SUCCESS] Saved screenshot to {proof}!", flush=True)

if __name__ == "__main__":
    asyncio.run(run())
