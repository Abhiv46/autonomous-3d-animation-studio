import asyncio
from playwright.async_api import async_playwright

VID_ID = "j98zuoqOngk"
YT_TITLE = '"Meri Patang Atak Gayi!" 🪁😱 Mummy Ne Bachaya! 🥰😂 #TheNaughtyDuo #shorts'
YT_DESC = (
    "Kaartik bhaiyya ki favourite laal patang hawa me udd ke unche ped par atak gayi! 🪁😱\n"
    "Phir Mummy aur Kaavya ne milkar banaya ek super rescue plan! Dekhiye kya patang wapas mili? 🥰❤️\n\n"
    "Aapki patang kabhi ped ya chatt par atki hai kya? Comment me batayein! 👇😂🪁\n\n"
    "Aise hi cute aur funny 3D family cartoon stories ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔✨\n\n"
    "#TheNaughtyDuo #shorts #viral #funny #kiteflying #patang #patangbazi #3danimation #hindicartoon #kidsanimation #trending #comedy #family #ytshorts"
)

async def finalize():
    print(f"[1] Connecting to browser for video {VID_ID}...", flush=True)
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = [pg for pg in b.contexts[0].pages if "studio.youtube.com" in pg.url][0]
        
        edit_url = f"https://studio.youtube.com/video/{VID_ID}/edit"
        print(f"[2] Navigating to edit page: {edit_url}", flush=True)
        await page.goto(edit_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)
        
        # 1. Title box
        print("[3] Checking / updating Title...", flush=True)
        title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        if await title_box.count() > 0:
            await title_box.click()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await title_box.fill(YT_TITLE[:100])
            await page.wait_for_timeout(500)
            print("[+] Title set!", flush=True)
            
        # 2. Description box
        print("[4] Checking / updating Description...", flush=True)
        desc_box = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
        if await desc_box.count() > 0:
            await desc_box.click()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await desc_box.fill(YT_DESC)
            await page.wait_for_timeout(500)
            print("[+] Description set!", flush=True)

        # 3. Audience: Not made for kids
        print("[5] Setting Audience to Not Made for Kids...", flush=True)
        not_kids = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
        if await not_kids.count() > 0:
            await not_kids.click(force=True)
            print("[+] Audience set: Not made for kids.", flush=True)
            await page.wait_for_timeout(500)

        # 4. Visibility to Public
        print("[6] Updating Visibility to PUBLIC...", flush=True)
        vis_trigger = page.locator("#visibility-trigger, [aria-label*='Visibility' i], ytcp-video-visibility-select").first
        if await vis_trigger.count() > 0:
            await vis_trigger.click()
            await page.wait_for_timeout(1000)
            
            pub_radio = page.locator("tp-yt-paper-radio-button[name='PUBLIC'], [aria-label*='Public']").first
            if await pub_radio.count() > 0:
                await pub_radio.click(force=True)
                print("[+] Public radio clicked!", flush=True)
                await page.wait_for_timeout(500)
                
            save_vis = page.locator("button:has-text('Save'), ytcp-button:has-text('Save'), ytcp-button#save-button").first
            if await save_vis.count() > 0 and await save_vis.is_visible():
                await save_vis.click(force=True)
                print("[+] Clicked Save on visibility dropdown!", flush=True)
                await page.wait_for_timeout(1000)

        # 5. Top Save Button
        print("[7] Clicking main Save button...", flush=True)
        save_btn = page.locator("button#save, ytcp-button#save-button, button:has-text('Save')").first
        if await save_btn.count() > 0 and await save_btn.is_enabled():
            await save_btn.click(force=True)
            print("[+] Clicked main Save button!", flush=True)
            await page.wait_for_timeout(4000)
            
        # Proof screenshot of edit page
        proof_edit = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_kite_edit_saved.png"
        await page.screenshot(path=proof_edit)
        print(f"[+] Edit page screenshot saved to {proof_edit}", flush=True)
        
        # Go to channel shorts list
        print("[8] Navigating to Shorts channel list...", flush=True)
        await page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)
        
        proof_list = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_kite_public_confirmed.png"
        await page.screenshot(path=proof_list)
        print(f"[SUCCESS] Final confirmation screenshot saved to {proof_list}", flush=True)

if __name__ == "__main__":
    asyncio.run(finalize())
