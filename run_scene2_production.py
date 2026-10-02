import asyncio
from playwright.async_api import async_playwright

SCENE2_PROMPT = (
    "Pure 3D animated cartoon style. Kaartik comically wags his finger like a dramatic strict parent, frowning playfully. "
    "Kaavya wobbles unsteadily in Mummy's giant pink high heels, making an adorable guilty pout with huge glossy eyes as she balances. "
    "Bright cheerful Pixar cartoon animation, expressive facial expressions, cozy sunny bedroom."
)

async def generate_scene2():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = browser.contexts[0].pages[0]
        
        print("[1] Opening Add Ingredients menu...", flush=True)
        add_btn = page.locator("button[aria-label='Add ingredients to the prompt box']").first
        await add_btn.click()
        await page.wait_for_timeout(1500)
        
        # Select 'Boy and girl playing dressup'
        print("[2] Selecting 'Boy and girl playing dressup' image...", flush=True)
        img_item = page.locator("text='Boy and girl playing dressup'").first
        await img_item.click()
        await page.wait_for_timeout(1000)
        
        # Add character Kaartik
        print("[3] Adding Kaartik character...", flush=True)
        await add_btn.click()
        await page.wait_for_timeout(1500)
        char_item = page.locator("text='Kaartik'").first
        await char_item.click()
        await page.wait_for_timeout(1000)
        
        # Type the prompt
        print("[4] Typing Scene 2 prompt...", flush=True)
        editor = page.locator(".ProseMirror, [contenteditable='true']").first
        await editor.click()
        await editor.fill(SCENE2_PROMPT)
        await page.wait_for_timeout(1000)
        
        # Click Start generation
        print("[5] Submitting generation...", flush=True)
        arrow_btn = page.locator("button.start-generation-button, button[aria-label='Start generation']").first
        if await arrow_btn.count() > 0 and await arrow_btn.is_enabled():
            await arrow_btn.click()
        else:
            await page.keyboard.press("Control+Enter")
        
        await page.wait_for_timeout(3000)
        
        # Check for I2V option dialog ("Animate just the image (I2V)")
        print("[6] Checking for I2V option...", flush=True)
        i2v_btn = page.locator("text='Animate just the image (I2V)', button:has-text('Animate just the image')").first
        if await i2v_btn.count() > 0 and await i2v_btn.is_visible():
            print("[+] Clicking 'Animate just the image (I2V)'...", flush=True)
            await i2v_btn.click()
            await page.wait_for_timeout(2000)
            
            # Check confirm/continue if any
            conf = page.locator("button:has-text('Confirm'), button:has-text('Submit'), button:has-text('Continue')").first
            if await conf.count() > 0 and await conf.is_visible():
                await conf.click()
                await page.wait_for_timeout(2000)
        
        # Check approval dialog
        approve_btn = page.locator("button:has-text('Approve'), button:has-text('Always approve')").first
        if await approve_btn.count() > 0 and await approve_btn.is_visible():
            print("[+] Clicking Approve...", flush=True)
            await approve_btn.click()
            await page.wait_for_timeout(2000)
        
        await page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\scene2_submitted.png")
        print("[✓] Submission complete! Screenshot saved.", flush=True)

asyncio.run(generate_scene2())
