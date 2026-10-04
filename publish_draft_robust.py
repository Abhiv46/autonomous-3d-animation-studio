import asyncio
from playwright.async_api import async_playwright

VID_ID = "j98zuoqOngk"

async def publish():
    print(f"Connecting to CDP...", flush=True)
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = [pg for pg in b.contexts[0].pages if "studio.youtube.com" in pg.url][0]
        
        edit_url = f"https://studio.youtube.com/video/{VID_ID}/edit"
        print(f"Navigating to {edit_url}...", flush=True)
        await page.goto(edit_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # Click "Edit draft" button at top
        print("Looking for Edit draft button...", flush=True)
        edit_draft_btn = page.locator("button:has-text('Edit draft'), ytcp-button:has-text('Edit draft')").first
        if await edit_draft_btn.count() > 0 and await edit_draft_btn.is_visible():
            await edit_draft_btn.click()
            print("Clicked Edit draft button!", flush=True)
            await page.wait_for_timeout(3000)
        else:
            print("Edit draft button not found, checking if dialog open...")

        # Screenshot dialog
        dialog = page.locator("ytcp-uploads-dialog")
        await dialog.wait_for(timeout=10000)
        print("Upload dialog is open!", flush=True)
        
        # Step through wizard
        for step in range(4):
            # Check if we are on visibility step
            pub_radio = dialog.locator("tp-yt-paper-radio-button[name='PUBLIC']").first
            if await pub_radio.count() > 0 and await pub_radio.is_visible():
                print("Found Visibility step!", flush=True)
                await pub_radio.click(force=True)
                print("Selected Public radio button!", flush=True)
                await page.wait_for_timeout(1000)
                break
                
            next_btn = dialog.locator("ytcp-button#next-button, button:has-text('Next')").first
            if await next_btn.count() > 0 and await next_btn.is_visible() and await next_btn.is_enabled():
                await next_btn.click(force=True)
                print(f"Clicked Next (Step {step+1})", flush=True)
                await page.wait_for_timeout(2500)

        await page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\draft_step_visibility.png")

        # Click Publish / Done / Save
        print("Finding Publish/Save button in dialog...", flush=True)
        publish_btn = dialog.locator("ytcp-button#done-button, button:has-text('Publish'), button:has-text('Save'), #publish-button").first
        if await publish_btn.count() > 0 and await publish_btn.is_visible():
            print("Clicking Publish button...", flush=True)
            await publish_btn.click(force=True)
            await page.wait_for_timeout(4000)
            
        # Check if Publish anyway button appears
        pub_anyway = page.locator("button:has-text('Publish anyway'), ytcp-button:has-text('Publish anyway')").first
        if await pub_anyway.count() > 0 and await pub_anyway.is_visible():
            print("Clicked Publish anyway!", flush=True)
            await pub_anyway.click(force=True)
            await page.wait_for_timeout(4000)

        await page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\draft_after_publish_click.png")

        # Close dialog if close button visible
        close_btn = page.locator("ytcp-button#close-button, button:has-text('Close')").first
        if await close_btn.count() > 0 and await close_btn.is_visible():
            await close_btn.click(force=True)
            await page.wait_for_timeout(2000)

        # Go to channel shorts list
        await page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        await page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\draft_final_channel_shorts.png")
        print("All done!")

if __name__ == "__main__":
    asyncio.run(publish())
