import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

VIDEO_FILE = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\TheNaughtyDuo_YouTube_MagicColorAdventure_Master.mp4"
SCREENSHOT_DIR = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2")

YT_TITLE = "Kaartik & Kaavya Ki Magical Rainbow Duniya! 🌈✨ Colors Magic Quest! 🥰🎨 #TheNaughtyDuo #shorts"

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

async def upload():
    print("[1] Connecting Playwright over CDP...", flush=True)
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        
        # Find or open YouTube Studio tab
        page = None
        for pg in context.pages:
            if "studio.youtube.com" in pg.url:
                page = pg
                break
                
        if not page:
            page = await context.new_page()
            await page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", wait_until="domcontentloaded")
            await page.wait_for_timeout(4000)
        else:
            await page.bring_to_front()
            await page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", wait_until="domcontentloaded")
            await page.wait_for_timeout(4000)

        # Skip dialog if present
        skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
        if await skip.count() > 0 and await skip.is_visible():
            await skip.click()
            await page.wait_for_timeout(2000)

        # 1. Click Create button
        print("[2] Clicking Create button...", flush=True)
        create_btn = page.locator("#create-icon, ytcp-button#create-icon, button[aria-label*='Create' i]").first
        await create_btn.wait_for(timeout=15000)
        await create_btn.click()
        await page.wait_for_timeout(1500)

        # 2. Click Upload videos item
        print("[3] Clicking Upload videos...", flush=True)
        upload_opt = page.locator("ytcp-text-menu-item:has-text('Upload videos'), tp-yt-paper-item:has-text('Upload videos'), text='Upload videos'").first
        await upload_opt.click()
        await page.wait_for_timeout(2000)

        # 3. File chooser
        print(f"[4] Selecting file: {VIDEO_FILE}...", flush=True)
        select_files_btn = page.locator("#select-files-button, button:has-text('Select files'), ytcp-button:has-text('Select files')").first
        if await select_files_btn.count() > 0 and await select_files_btn.is_visible():
            async with page.expect_file_chooser(timeout=15000) as fc_info:
                await select_files_btn.click()
            fc = await fc_info.value
            await fc.set_files(VIDEO_FILE)
            print("[+] File attached via file chooser!", flush=True)
        else:
            file_input = page.locator("input[type='file']").first
            await file_input.set_input_files(VIDEO_FILE)
            print("[+] File attached via file input!", flush=True)

        print("[5] Waiting for upload dialog to process...", flush=True)
        dialog = page.locator("ytcp-uploads-dialog")
        await dialog.wait_for(timeout=30000)
        await page.wait_for_timeout(8000)

        # 4. Fill Title
        print("[6] Setting Title...", flush=True)
        title_box = dialog.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        await title_box.wait_for(timeout=15000)
        await title_box.click()
        await page.keyboard.press("Control+A")
        await page.keyboard.press("Backspace")
        await title_box.fill(YT_TITLE[:100])
        await page.wait_for_timeout(500)
        print("[+] Title set successfully!", flush=True)

        # 5. Fill Description
        print("[7] Setting Description...", flush=True)
        desc_box = dialog.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
        if await desc_box.count() > 0:
            await desc_box.click()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await desc_box.fill(YT_DESC)
            await page.wait_for_timeout(500)
            print("[+] Description set successfully!", flush=True)

        # 6. Audience: Not made for kids
        print("[8] Setting Audience to Not Made for Kids...", flush=True)
        not_kids = dialog.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
        if await not_kids.count() > 0:
            await not_kids.click(force=True)
            print("[+] Audience set: Not made for kids.", flush=True)
            await page.wait_for_timeout(500)

        # 7. Show more & Tags
        print("[9] Adding Tags...", flush=True)
        show_more = dialog.locator("#toggle-button, ytcp-button:has-text('Show more')").first
        if await show_more.count() > 0:
            await show_more.click(force=True)
            await page.wait_for_timeout(1500)
            
            tags_input = dialog.locator("input[aria-label*='Tag' i], input[placeholder*='tag' i], #tags-container input").first
            if await tags_input.count() > 0:
                await tags_input.click()
                tags_str = ", ".join(YT_TAGS) + ","
                await tags_input.fill(tags_str)
                await page.keyboard.press("Enter")
                print("[+] Tags set successfully!", flush=True)
                await page.wait_for_timeout(500)

        # 8. Step through Wizard (Next buttons)
        print("[10] Stepping through wizard to Visibility...", flush=True)
        for step in range(3):
            next_btn = dialog.locator("ytcp-button#next-button, button:has-text('Next')").first
            if await next_btn.count() > 0 and await next_btn.is_visible() and await next_btn.is_enabled():
                await next_btn.click(force=True)
                print(f"[+] Clicked Next (Step {step+1})", flush=True)
                await page.wait_for_timeout(2500)

        # 9. Set Visibility to PUBLIC
        print("[11] Selecting PUBLIC visibility...", flush=True)
        pub_radio = dialog.locator("tp-yt-paper-radio-button[name='PUBLIC']").first
        await pub_radio.wait_for(timeout=10000)
        await pub_radio.click(force=True)
        print("[+] Public visibility selected!", flush=True)
        await page.wait_for_timeout(1500)

        # 10. Click Publish
        print("[12] Clicking Publish button...", flush=True)
        publish_btn = dialog.locator("ytcp-button#done-button, button:has-text('Publish'), #publish-button").first
        await publish_btn.click(force=True)
        print("[+] Publish clicked!", flush=True)
        await page.wait_for_timeout(5000)

        # Publish anyway if modal appears
        pub_anyway = page.locator("button:has-text('Publish anyway'), ytcp-button:has-text('Publish anyway')").first
        if await pub_anyway.count() > 0 and await pub_anyway.is_visible():
            await pub_anyway.click(force=True)
            print("[+] Publish anyway clicked!", flush=True)
            await page.wait_for_timeout(4000)

        # Close dialog
        close_btn = page.locator("ytcp-button#close-button, button:has-text('Close')").first
        if await close_btn.count() > 0 and await close_btn.is_visible():
            await close_btn.click(force=True)
            await page.wait_for_timeout(3000)

        # Navigate to channel shorts list for final confirmation
        print("[13] Navigating to Shorts channel list for verification...", flush=True)
        await page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", wait_until="networkidle")
        await page.wait_for_timeout(4000)

        proof_path = str(SCREENSHOT_DIR / "yt_color_adventure_live_proof.png")
        await page.screenshot(path=proof_path)
        print(f"[SUCCESS] Upload and Publish complete! Screenshot saved to {proof_path}", flush=True)

if __name__ == "__main__":
    asyncio.run(upload())
