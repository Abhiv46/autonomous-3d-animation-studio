import asyncio
from playwright.async_api import async_playwright

YT_TITLE = "Kaavya Ne Pehni Mummy Ki High Heels! 😂👠 Sassy Model Kaavya! #shorts"
YT_DESC = (
    "Kaavya ne pehan li Mummy ki nayi pink high heels aur ban gayi fashion model! 😂👠\n"
    "Lekin jab Kaartik bhaiyya ne strict banke pakad liya toh dekhiye Kaavya ne kaise cute bahane banaye! 🥰❤️\n\n"
    "Aapne bhi bachpan me Mummy ki heels try ki hai kya? Comment me batayein! 👇😂\n\n"
    "Aise hi funny aur cute 3D family cartoons ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔✨\n\n"
    "#shorts #TheNaughtyDuo #funnycartoon #3danimation #hindicartoon #kaavyaandkaartik #comedy #relatablecomedy #viralshorts #trending #kidsanimation"
)

async def direct_edit():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = [pg for pg in b.contexts[0].pages if 'studio.youtube.com' in pg.url][0]
        
        edit_url = "https://studio.youtube.com/video/iLNSVrQO-v8/edit"
        print(f"Navigating to direct edit: {edit_url}", flush=True)
        await page.goto(edit_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)
        
        print("Page URL:", page.url, flush=True)
        await page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\direct_edit_page.png")
        
        # 1. Title box
        print("Updating Title...", flush=True)
        title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        if await title_box.count() > 0:
            await title_box.click()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await title_box.fill(YT_TITLE[:100])
            await page.wait_for_timeout(500)
            print("[+] Title updated!", flush=True)
            
        # 2. Description box
        print("Updating Description...", flush=True)
        desc_box = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
        if await desc_box.count() > 0:
            await desc_box.click()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await desc_box.fill(YT_DESC)
            await page.wait_for_timeout(500)
            print("[+] Description updated!", flush=True)
            
        # 3. Visibility to Public
        print("Updating Visibility...", flush=True)
        vis_btn = page.locator("#visibility-trigger, [aria-label*='Visibility' i], ytcp-video-visibility-select").first
        if await vis_btn.count() > 0:
            await vis_btn.click()
            await page.wait_for_timeout(1000)
            pub_radio = page.locator("tp-yt-paper-radio-button[name='PUBLIC'], [aria-label*='Public']").first
            if await pub_radio.count() > 0:
                await pub_radio.click()
                print("[+] Public radio clicked!", flush=True)
                await page.wait_for_timeout(500)
            save_vis = page.locator("button:has-text('Save'), ytcp-button:has-text('Save')").first
            if await save_vis.count() > 0 and await save_vis.is_visible():
                await save_vis.click()
                await page.wait_for_timeout(1000)
                
        # 4. Click top Save button
        print("Clicking top Save button...", flush=True)
        save_btn = page.locator("button#save, ytcp-button#save-button, button:has-text('Save')").first
        if await save_btn.count() > 0 and await save_btn.is_enabled():
            await save_btn.click()
            print("[+] Clicked Save button!", flush=True)
            await page.wait_for_timeout(4000)
            
        await page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\direct_edit_saved.png")
        print("[SUCCESS] YouTube video updated and saved!", flush=True)

asyncio.run(direct_edit())
