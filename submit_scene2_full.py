import asyncio
from playwright.async_api import async_playwright

SCENE2_PROMPT = (
    "Pure 3D animated cartoon style. Kaartik comically wags his finger like a dramatic strict parent, frowning playfully. "
    "Kaavya wobbles unsteadily in Mummy's giant pink high heels, making an adorable guilty pout with huge glossy eyes as she balances. "
    "Bright cheerful Pixar cartoon animation, expressive facial expressions, cozy sunny bedroom."
)

async def submit_scene2():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = browser.contexts[0].pages[0]
        
        # 1. Click + to add character
        print("[1] Opening add ingredients for character...", flush=True)
        add_btn = page.locator("button[aria-label='Add ingredients to the prompt box']").first
        await add_btn.click()
        await page.wait_for_timeout(1500)
        
        # 2. Select Kaavya character in overlay
        print("[2] Selecting Kaavya character...", flush=True)
        overlay = page.locator('.cdk-overlay-container')
        char_item = overlay.locator("text='Kaavya'").first
        if await char_item.count() > 0:
            await char_item.click()
            print("[+] Added Kaavya character!", flush=True)
            await page.wait_for_timeout(1000)
        else:
            print("[-] Kaavya character not found in overlay", flush=True)
            
        # 3. Focus editor and enter prompt
        print("[3] Entering pure 3D animated prompt...", flush=True)
        editor = page.locator(".ProseMirror, [contenteditable='true']").first
        await editor.click()
        await page.keyboard.type(SCENE2_PROMPT, delay=5)
        await page.wait_for_timeout(1500)
        
        # Take screenshot before submit
        await page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\scene2_ready_to_send.png")
        print("[4] Screenshot saved before sending", flush=True)
        
        # 4. Click Start generation (arrow button)
        print("[5] Submitting generation...", flush=True)
        arrow_btn = page.locator("button.start-generation-button, button[aria-label='Start generation']").first
        if await arrow_btn.count() > 0 and await arrow_btn.is_enabled():
            await arrow_btn.click()
        else:
            await page.keyboard.press("Control+Enter")
        
        await page.wait_for_timeout(3000)
        
        # 5. Check if 2 options dialog appeared ("Animate just the image (I2V)" vs R2V)
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
            
        # 6. Check for Approve dialog
        print("[7] Checking for Approve dialog...", flush=True)
        approve_btn = page.locator("button:has-text('Approve'), button:has-text('Always approve')").first
        if await approve_btn.count() > 0 and await approve_btn.is_visible():
            print("[+] Clicking Approve button...", flush=True)
            await approve_btn.click()
            await page.wait_for_timeout(2000)
            
        await page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\scene2_generation_started.png")
        print("[✓] Scene 2 generation started successfully!", flush=True)

asyncio.run(submit_scene2())
