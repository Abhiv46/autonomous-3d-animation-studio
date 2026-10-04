import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = [pg for pg in b.contexts[0].pages if "studio.youtube.com" in pg.url][0]

        # Press Escape key multiple times to dismiss any hashtag popup or overlay
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(300)
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(500)

        # Look for the Save button at the top
        save_btn = page.locator("ytcp-button#save-button button, button#save, #save-button button").first
        if await save_btn.count() > 0:
            is_disabled = await save_btn.get_attribute("disabled")
            aria_disabled = await save_btn.get_attribute("aria-disabled")
            print(f"Save button found. disabled={is_disabled}, aria-disabled={aria_disabled}", flush=True)
            if is_disabled is None and aria_disabled != "true":
                await save_btn.click(force=True)
                print("[+] Clicked Save button successfully!", flush=True)
            else:
                print("[*] Save button is already disabled (changes might already be saved)!", flush=True)
        else:
            print("[-] Save button not found via locator, trying JS click...", flush=True)
            await page.evaluate("""() => {
                const btn = document.querySelector('ytcp-button#save-button, button#save');
                if (btn) btn.click();
            }""")

        await page.wait_for_timeout(3000)

        out_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_color_final_saved_success.png"
        await page.screenshot(path=out_path)
        print(f"[SUCCESS] Screenshot saved to {out_path}!", flush=True)

if __name__ == "__main__":
    asyncio.run(run())
