import asyncio
from playwright.async_api import async_playwright

VID_ID = "j98zuoqOngk"

TAGS = [
    "The Naughty Duo",
    "TheNaughtyDuo",
    "Kaartik and Kaavya",
    "patang",
    "kite flying",
    "patang bazi",
    "patang uddana",
    "patang atak gayi",
    "hindi cartoon",
    "3d animation",
    "funny cartoon hindi",
    "kids animation",
    "comedy shorts",
    "relatable comedy",
    "shorts",
    "viral shorts",
    "trending shorts",
    "cartoon shorts"
]

async def add_tags():
    print(f"Connecting to CDP for video {VID_ID}...", flush=True)
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = [pg for pg in b.contexts[0].pages if "studio.youtube.com" in pg.url][0]
        
        edit_url = f"https://studio.youtube.com/video/{VID_ID}/edit"
        print(f"Navigating to {edit_url}...", flush=True)
        await page.goto(edit_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3500)
        
        # Click "Show more" button if visible
        show_more = page.locator("#toggle-button, ytcp-button:has-text('Show more'), button:has-text('Show more')").first
        if await show_more.count() > 0 and await show_more.is_visible():
            await show_more.click()
            print("Clicked 'Show more' button!", flush=True)
            await page.wait_for_timeout(1500)
            
        # Locate tags input
        tags_input = page.locator("input[aria-label*='Tag' i], input[placeholder*='tag' i], #tags-container input").first
        if await tags_input.count() > 0:
            print("Found Tags input field!", flush=True)
            await tags_input.click()
            await page.wait_for_timeout(300)
            
            # Enter tags separated by comma
            tags_string = ", ".join(TAGS) + ","
            print(f"Adding tags: {tags_string}", flush=True)
            await tags_input.fill(tags_string)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(1000)
            print("Tags filled successfully!", flush=True)
        else:
            print("[!] Tags input not found directly, searching in DOM...")
            
        # Click top Save button
        save_btn = page.locator("button#save, ytcp-button#save-button, button:has-text('Save')").first
        if await save_btn.count() > 0 and await save_btn.is_enabled():
            await save_btn.click()
            print("Clicked main Save button!", flush=True)
            await page.wait_for_timeout(3500)
        else:
            print("Save button was not enabled or not found!")

        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_kite_tags_added_proof.png"
        await page.screenshot(path=proof_path)
        print(f"[SUCCESS] Proof screenshot saved to {proof_path}!", flush=True)

if __name__ == "__main__":
    asyncio.run(add_tags())
