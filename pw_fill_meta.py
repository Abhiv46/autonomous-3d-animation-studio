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

YT_TAGS = [
    "The Naughty Duo", "TheNaughtyDuo", "Kaartik and Kaavya", "learn colors hindi",
    "color song", "rainbow cartoon", "3d animation hindi", "hindi cartoon funny",
    "kids animation", "nursery rhyme hindi", "cartoon for toddlers", "relatable comedy",
    "shorts", "viral shorts", "trending shorts"
]

async def update_desc():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = [pg for pg in b.contexts[0].pages if "studio.youtube.com" in pg.url][0]
        
        edit_url = f"https://studio.youtube.com/video/{VID_ID}/edit"
        print(f"Navigating to {edit_url}...", flush=True)
        await page.goto(edit_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # 1. Fill Description
        desc_box = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
        if await desc_box.count() > 0:
            await desc_box.click()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await desc_box.fill(YT_DESC)
            print("[+] Description filled successfully!", flush=True)
            await page.wait_for_timeout(500)
            
        # 2. Click Show more & Add tags
        show_more = page.locator("#toggle-button, ytcp-button:has-text('Show more')").first
        if await show_more.count() > 0 and await show_more.is_visible():
            await show_more.click()
            print("[+] Clicked Show more!", flush=True)
            await page.wait_for_timeout(1000)
            
        tags_input = page.locator("input[aria-label*='Tag' i], input[placeholder*='tag' i], #tags-container input").first
        if await tags_input.count() > 0:
            await tags_input.click()
            tags_str = ", ".join(YT_TAGS) + ","
            await tags_input.fill(tags_str)
            await page.keyboard.press("Enter")
            print("[+] Tags set successfully!", flush=True)
            await page.wait_for_timeout(500)

        # 3. Click Save button
        save_btn = page.locator("button#save, ytcp-button#save-button").first
        if await save_btn.count() > 0 and await save_btn.is_enabled():
            await save_btn.click()
            print("[+] Save button clicked!", flush=True)
            await page.wait_for_timeout(4000)
        else:
            print("[!] Save button not enabled or found!")

        proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_color_desc_and_tags_confirmed.png"
        await page.screenshot(path=proof)
        print(f"[SUCCESS] Proof saved to {proof}!", flush=True)

if __name__ == "__main__":
    asyncio.run(update_desc())
