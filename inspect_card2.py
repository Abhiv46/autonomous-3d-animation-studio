import asyncio
from playwright.async_api import async_playwright

async def check_credits_and_card2():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = [pg for pg in browser.contexts[0].pages if 'flow.google.com' in pg.url][0]
        
        # Click PRO / Account details to check credits
        account_btn = page.get_by_role("button", name="Account details")
        if await account_btn.is_visible():
            await account_btn.click()
            await page.wait_for_timeout(1500)
            dialog_text = await page.locator("div[role='dialog'], [role='menu'], div[class*='popover'], div[class*='panel']").all_inner_texts()
            print("Credits Dialog:", dialog_text)
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(1000)
        
        # Click on "Toddler walking in oversized shoes"
        card2 = page.get_by_text("Toddler walking in oversized shoes").first
        if await card2.is_visible():
            print("Clicking Card 2...")
            await card2.click()
            await page.wait_for_timeout(3000)
            print("Card 2 URL:", page.url)
            await page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\card2_state.png")

asyncio.run(check_credits_and_card2())
