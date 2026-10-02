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

async def edit_and_publish():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = [pg for pg in b.contexts[0].pages if 'studio.youtube.com' in pg.url][0]
        
        # Click on the draft item (Row with 'TheNaughtyDuo EP21 MummyKiHi')
        print("[1] Clicking draft item to open editor...", flush=True)
        draft = page.locator("text='TheNaughtyDuo EP21 MummyKiHi'").first
        await draft.click()
        await page.wait_for_timeout(3000)
        print("Opened editor. URL:", page.url, flush=True)
        
        # Title
        print("[2] Setting title...", flush=True)
        title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        if await title_box.count() > 0:
            await title_box.click()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await title_box.fill(YT_TITLE[:100])
            await page.wait_for_timeout(500)
            print("[+] Title set!", flush=True)
            
        # Description
        print("[3] Setting description...", flush=True)
        desc_box = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
        if await desc_box.count() > 0:
            await desc_box.click()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await desc_box.fill(YT_DESC)
            await page.wait_for_timeout(500)
            print("[+] Description set!", flush=True)
            
        # Check Visibility / Save button
        print("[4] Checking visibility and publishing...", flush=True)
        # Look for visibility dropdown or radio
        vis_trigger = page.locator("#visibility-trigger, [aria-label*='Visibility' i]").first
        if await vis_trigger.count() > 0 and await vis_trigger.is_visible():
            await vis_trigger.click()
            await page.wait_for_timeout(1000)
            pub_radio = page.locator("tp-yt-paper-radio-button[name='PUBLIC'], [aria-label*='Public']").first
            if await pub_radio.count() > 0:
                await pub_radio.click()
                print("[+] Selected Public visibility", flush=True)
                await page.wait_for_timeout(500)
            save_vis = page.locator("button:has-text('Save'), ytcp-button:has-text('Save')").first
            if await save_vis.count() > 0:
                await save_vis.click()
                await page.wait_for_timeout(1000)
                
        # Main save button on top right of video details
        save_btn = page.locator("button#save, ytcp-button#save-button, button:has-text('Save')").first
        if await save_btn.count() > 0 and await save_btn.is_enabled():
            await save_btn.click()
            print("[+] Clicked Save button!", flush=True)
            await page.wait_for_timeout(3000)
            
        # Capture screenshot
        await page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_draft_published.png")
        print("[SUCCESS] YouTube video details saved & published!", flush=True)

asyncio.run(edit_and_publish())
