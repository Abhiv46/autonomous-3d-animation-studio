import asyncio
import json
from playwright.async_api import async_playwright

VID_ID = "j98zuoqOngk"
YT_DESC = (
    "Kaartik bhaiyya ki favourite laal patang hawa me udd ke unche ped par atak gayi! 🪁😱\n"
    "Phir Mummy aur Kaavya ne milkar banaya ek super rescue plan! Dekhiye kya patang wapas mili? 🥰❤️\n\n"
    "Aapki patang kabhi ped ya chatt par atki hai kya? Comment me batayein! 👇😂🪁\n\n"
    "Aise hi cute aur funny 3D family cartoon stories ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔✨\n\n"
    "#TheNaughtyDuo #shorts #viral #funny #kiteflying #patang #patangbazi #3danimation #hindicartoon #kidsanimation #trending #comedy #family #ytshorts"
)

async def set_desc():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = [pg for pg in b.contexts[0].pages if "studio.youtube.com" in pg.url][0]
        
        edit_url = f"https://studio.youtube.com/video/{VID_ID}/edit"
        print(f"Navigating to {edit_url}...", flush=True)
        await page.goto(edit_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        desc_box = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
        if await desc_box.count() > 0:
            await desc_box.click()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await desc_box.fill(YT_DESC)
            await page.wait_for_timeout(500)
            print("[+] Description filled successfully!", flush=True)
            
        save_btn = page.locator("button#save, ytcp-button#save-button").first
        if await save_btn.count() > 0 and await save_btn.is_enabled():
            await save_btn.click()
            print("[+] Save button clicked!", flush=True)
            await page.wait_for_timeout(3000)

        # Go to channel shorts list
        await page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_kite_live_public_with_desc.png"
        await page.screenshot(path=proof)
        print(f"[SUCCESS] Final proof with description saved to {proof}!", flush=True)

if __name__ == "__main__":
    asyncio.run(set_desc())
