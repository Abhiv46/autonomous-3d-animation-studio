import asyncio
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright

VIDEO_FILE = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\TheNaughtyDuo_TikTok_KiteAdventure_Master.mp4"
SCREENSHOT_DIR = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2")

YT_TITLE = '"Meri Patang Atak Gayi!" 🪁😱 Kaartik & Mummy Ka Crazy Rescue! 🥰😂 #TheNaughtyDuo #shorts'
YT_DESC = (
    "Kaartik bhaiyya ki favourite laal patang hawa me udd ke unche ped par atak gayi! 🪁😱\n"
    "Phir Mummy aur Kaavya ne milkar banaya ek super rescue plan! Dekhiye kya patang wapas mili? 🥰❤️\n\n"
    "Aapki patang kabhi ped ya chatt par atki hai kya? Comment me batayein! 👇😂🪁\n\n"
    "Aise hi cute aur funny 3D family cartoon stories ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔✨\n\n"
    "#TheNaughtyDuo #shorts #viral #funny #kiteflying #patang #patangbazi #3danimation #hindicartoon #kidsanimation #trending #comedy #family #ytshorts"
)

async def upload():
    print("[1] Connecting to browser via CDP...", flush=True)
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        
        # Check if an existing YouTube Studio page is open, otherwise create new
        page = None
        for pg in context.pages:
            if "studio.youtube.com" in pg.url:
                page = pg
                print(f"[+] Found existing YouTube Studio tab: {pg.url}", flush=True)
                break
        
        if not page:
            print("[+] Opening new page for YouTube Studio...", flush=True)
            page = await context.new_page()
            await page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_timeout(3000)
        else:
            await page.bring_to_front()
            # If on content tab, ensure ready
            if "dialog" not in page.url and await page.locator("ytcp-uploads-dialog").count() == 0:
                await page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)

        # Skip dialog if present
        skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
        if await skip.count() > 0 and await skip.is_visible():
            print("[+] Clicking Skip to YouTube Studio...", flush=True)
            await skip.click()
            await page.wait_for_timeout(2000)

        # Check if dialog is already open
        dialog = page.locator("ytcp-uploads-dialog")
        if await dialog.count() == 0:
            print("[2] Opening upload dialog...", flush=True)
            create_btn = page.locator("#create-icon, ytcp-button#create-icon, button[aria-label*='Create' i]").first
            if await create_btn.count() > 0:
                await create_btn.click()
                await page.wait_for_timeout(1500)
                
                upload_option = page.get_by_text("Upload videos", exact=False).first
                if await upload_option.count() > 0 and await upload_option.is_visible():
                    await upload_option.click()
                await page.wait_for_timeout(2500)

        # Upload file
        print("[3] Selecting file to upload...", flush=True)
        select_files_btn = page.locator("#select-files-button, button:has-text('Select files'), ytcp-button:has-text('Select files')").first
        if await select_files_btn.count() > 0 and await select_files_btn.is_visible():
            async with page.expect_file_chooser(timeout=10000) as fc_info:
                await select_files_btn.click()
            fc = await fc_info.value
            await fc.set_files(VIDEO_FILE)
            print("[+] File selected via file chooser!", flush=True)
        else:
            file_input = page.locator("input[type='file']").first
            await file_input.set_input_files(VIDEO_FILE)
            print("[+] File selected via input[type='file']!", flush=True)

        print("[4] Waiting for upload dialog to populate...", flush=True)
        await page.wait_for_timeout(8000)
        
        # Detect video link
        video_link = None
        for _ in range(15):
            links = page.locator("a.ytcp-video-info, a[href*='youtu.be'], a[href*='youtube.com/shorts']")
            if await links.count() > 0:
                for idx in range(await links.count()):
                    href = await links.nth(idx).get_attribute("href")
                    if href and ("youtu.be" in href or "shorts" in href):
                        video_link = href
                        break
            if video_link:
                break
            await page.wait_for_timeout(1000)
        print(f"[+] Video Link: {video_link}", flush=True)

        # Fill Title
        print("[5] Filling Title...", flush=True)
        title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        if await title_box.count() > 0:
            await title_box.click()
            await page.wait_for_timeout(300)
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await title_box.fill(YT_TITLE[:100])
            await page.wait_for_timeout(500)
            print("[+] Title populated successfully!", flush=True)

        # Fill Description
        print("[6] Filling Description...", flush=True)
        desc_box = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
        if await desc_box.count() > 0:
            await desc_box.click()
            await page.wait_for_timeout(300)
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await desc_box.fill(YT_DESC)
            await page.wait_for_timeout(500)
            print("[+] Description populated successfully!", flush=True)

        # Audience: Not made for kids
        print("[7] Setting Audience...", flush=True)
        not_kids = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
        if await not_kids.count() > 0:
            await not_kids.click(force=True)
            print("[+] Audience set: Not made for kids.", flush=True)
            await page.wait_for_timeout(500)

        # Take screenshot of details
        await page.screenshot(path=str(SCREENSHOT_DIR / "yt_kite_details_filled.png"))
        print("[+] Details screenshot saved.", flush=True)

        # Wizard Steps (Next buttons)
        print("[8] Stepping through wizard...", flush=True)
        for step in range(3):
            next_btn = page.locator("ytcp-button#next-button, button:has-text('Next')").first
            if await next_btn.count() > 0 and await next_btn.is_visible() and await next_btn.is_enabled():
                await next_btn.click(force=True)
                print(f"[+] Clicked Next (Step {step+1})", flush=True)
                await page.wait_for_timeout(2500)

        # Visibility: PUBLIC
        print("[9] Setting Visibility to PUBLIC...", flush=True)
        pub_radio = page.locator("ytcp-uploads-dialog tp-yt-paper-radio-button[name='PUBLIC'], tp-yt-paper-radio-button[name='PUBLIC']").first
        if await pub_radio.count() > 0:
            await pub_radio.click(force=True)
            print("[+] Visibility selected: PUBLIC.", flush=True)
            await page.wait_for_timeout(1500)

        # Take screenshot before publish
        await page.screenshot(path=str(SCREENSHOT_DIR / "yt_kite_visibility_public.png"))

        # Publish
        print("[10] Clicking Publish button...", flush=True)
        publish_btn = page.locator("ytcp-uploads-dialog ytcp-button#done-button, ytcp-uploads-dialog button:has-text('Publish'), ytcp-uploads-dialog #publish-button").first
        if await publish_btn.count() == 0:
            publish_btn = page.locator("button:has-text('Publish')").first
        if await publish_btn.count() > 0:
            await publish_btn.click(force=True)
            print("[+] Clicked Publish!", flush=True)
            await page.wait_for_timeout(4000)

        # Publish anyway if modal appears
        pub_anyway = page.locator("button:has-text('Publish anyway'), ytcp-button:has-text('Publish anyway')").first
        if await pub_anyway.count() > 0 and await pub_anyway.is_visible():
            await pub_anyway.click(force=True)
            print("[+] Clicked Publish anyway!", flush=True)
            await page.wait_for_timeout(4000)

        # Close dialog / screenshot result
        close_btn = page.locator("ytcp-button#close-button, button:has-text('Close')").first
        if await close_btn.count() > 0 and await close_btn.is_visible():
            await page.screenshot(path=str(SCREENSHOT_DIR / "yt_kite_published_dialog.png"))
            await close_btn.click(force=True)
            await page.wait_for_timeout(3000)

        # Final screenshot on Shorts list
        await page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)
        await page.screenshot(path=str(SCREENSHOT_DIR / "yt_kite_final_shorts_list.png"))
        print("[SUCCESS] YouTube Shorts upload & publish complete! Screenshot saved.", flush=True)

if __name__ == "__main__":
    asyncio.run(upload())
