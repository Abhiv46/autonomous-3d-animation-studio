import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SCENE3_PROMPT = (
    "Pure 3D animated cartoon style. Kaavya dramatically flips her hair and poses sideways like a cute little fashion model in the mirror, laughing cheerfully. "
    "Kaartik sits on the bedroom carpet laughing joyfully at his little sister. "
    "Bright cheerful Pixar cartoon animation, expressive faces, cozy warm bedroom."
)
SAVE_PATH = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips\ep21_highheels_scene3_raw.mp4")

async def submit_scene3():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = browser.contexts[0].pages[0]
        
        # 1. Click + to add Scene 3 image
        print("[1] Opening add ingredients for image...", flush=True)
        add_btn = page.locator("button[aria-label='Add ingredients to the prompt box']").first
        await add_btn.click()
        await page.wait_for_timeout(1500)
        
        # 2. Select 'Toddler posing in high heels'
        print("[2] Selecting 'Toddler posing in high heels' image...", flush=True)
        overlay = page.locator('.cdk-overlay-container')
        img_item = overlay.locator("text='Toddler posing in high heels'").first
        if await img_item.count() > 0:
            await img_item.click()
            print("[+] Selected Scene 3 image!", flush=True)
            await page.wait_for_timeout(1500)
        else:
            print("[-] Scene 3 image not found", flush=True)
            
        # 3. Add Kaavya character
        print("[3] Adding Kaavya character...", flush=True)
        await add_btn.click()
        await page.wait_for_timeout(1500)
        char_item = overlay.locator("text='Kaavya'").first
        if await char_item.count() > 0:
            await char_item.click()
            print("[+] Added Kaavya character!", flush=True)
            await page.wait_for_timeout(1500)
            
        # 4. Focus editor and enter prompt
        print("[4] Entering pure 3D animated prompt for Scene 3...", flush=True)
        editor = page.locator(".ProseMirror, [contenteditable='true']").first
        await editor.click()
        await page.keyboard.type(SCENE3_PROMPT, delay=5)
        await page.wait_for_timeout(1500)
        
        # 5. Click Start generation
        print("[5] Submitting generation...", flush=True)
        arrow_btn = page.locator("button.start-generation-button, button[aria-label='Start generation']").first
        if await arrow_btn.count() > 0 and await arrow_btn.is_enabled():
            await arrow_btn.click()
        else:
            await page.keyboard.press("Control+Enter")
        
        await page.wait_for_timeout(3000)
        
        # 6. Check if 2 options dialog appeared ("Animate just the image (I2V)")
        print("[6] Checking for I2V selection...", flush=True)
        i2v_btn = page.locator("text='Animate just the image (I2V)', button:has-text('Animate just the image')").first
        if await i2v_btn.count() > 0 and await i2v_btn.is_visible():
            print("[+] Clicking 'Animate just the image (I2V)' option...", flush=True)
            await i2v_btn.click()
            await page.wait_for_timeout(2000)
            
            conf = page.locator("button:has-text('Confirm'), button:has-text('Submit'), button:has-text('Continue')").first
            if await conf.count() > 0 and await conf.is_visible():
                await conf.click()
                await page.wait_for_timeout(2000)
        else:
            print("No I2V selection dialog shown, proceeding directly", flush=True)
            
        # 7. Check for Approve dialog
        print("[7] Checking for Approve dialog...", flush=True)
        approve_btn = page.locator("button:has-text('Approve'), button:has-text('Always approve')").first
        if await approve_btn.count() > 0 and await approve_btn.is_visible():
            print("[+] Clicking Approve button...", flush=True)
            await approve_btn.click()
            await page.wait_for_timeout(2000)
            
        await page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\scene3_generation_started.png")
        print("[DONE] Scene 3 generation submitted!", flush=True)

asyncio.run(submit_scene3())
