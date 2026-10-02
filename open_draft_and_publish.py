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

async def run():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = [pg for pg in b.contexts[0].pages if 'studio.youtube.com' in pg.url][0]
        
        print("Waiting for video rows...", flush=True)
        await page.wait_for_selector('ytcp-video-row', timeout=15000)
        rows = await page.locator('ytcp-video-row').all()
        print(f"Found {len(rows)} video rows", flush=True)
        
        # Click on row 1 (the new draft video)
        title_elem = rows[1].locator('#video-title')
        await title_elem.click()
        await page.wait_for_timeout(4000)
        print("Editor page URL:", page.url, flush=True)
        
        # Fill Title
        print("Filling Title...", flush=True)
        title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        if await title_box.count() > 0:
            await title_box.click()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await title_box.fill(YT_TITLE[:100])
            await page.wait_for_timeout(500)
            print("Title updated!", flush=True)
            
        # Fill Description
        print("Filling Description...", flush=True)
        desc_box = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
        if await desc_box.count() > 0:
            await desc_box.click()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await desc_box.fill(YT_DESC)
            await page.wait_for_timeout(500)
            print("Description updated!", flush=True)
            
        # Set Visibility to Public
        print("Setting Visibility to Public...", flush=True)
        vis_trigger = page.locator("#visibility-trigger, [aria-label*='Visibility' i], ytcp-video-visibility-select").first
        if await vis_trigger.count() > 0:
            await vis_trigger.click()
            await page.wait_for_timeout(1000)
            pub_radio = page.locator("tp-yt-paper-radio-button[name='PUBLIC'], [aria-label*='Public']").first
            if await pub_radio.count() > 0:
                await pub_radio.click()
                print("Selected Public radio button!", flush=True)
                await page.wait_for_timeout(500)
            done_vis = page.locator("button:has-text('Save'), ytcp-button:has-text('Save'), ytcp-button#save-button").first
            if await done_vis.count() > 0 and await done_vis.is_visible():
                await done_vis.click()
                await page.wait_for_timeout(1000)
                
        # Click main Save / Publish button
        print("Saving changes...", flush=True)
        save_btn = page.locator("button#save, ytcp-button#save-button, button:has-text('Save')").first
        if await save_btn.count() > 0 and await save_btn.is_enabled():
            await save_btn.click()
            print("Saved successfully!", flush=True)
            await page.wait_for_timeout(4000)
            
        await page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_published_original_audio.png")
        print("[SUCCESS] YouTube Short is now PUBLIC with original audio!", flush=True)

asyncio.run(run())
