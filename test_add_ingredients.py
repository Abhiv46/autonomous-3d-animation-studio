import asyncio
from playwright.async_api import async_playwright

async def test_add():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = browser.contexts[0].pages[0]
        
        add_btn = page.locator("button[aria-label='Add ingredients to the prompt box']").first
        print("Add btn count:", await add_btn.count(), flush=True)
        await add_btn.click()
        await page.wait_for_timeout(1500)
        
        # Check what opened
        menu_items = await page.locator(".cdk-overlay-pane, [role='menu'], [role='dialog'], [role='menuitem']").all_inner_texts()
        print("Menu items:", menu_items, flush=True)
        
        await page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\add_ingredients_menu.png")
        await page.keyboard.press("Escape")

asyncio.run(test_add())
