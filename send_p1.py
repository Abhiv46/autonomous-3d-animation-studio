import asyncio
from playwright.async_api import async_playwright

async def send():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        flow_page = [pg for pg in b.contexts[0].pages if "flow.google.com/u/2" in pg.url][0]
        send_btn = flow_page.locator("button[aria-label*='Start generation' i], button:has-text('arrow_forward')").last
        await send_btn.click()
        print("Clicked Start Generation!")
        await flow_page.wait_for_timeout(3000)
        
        # Check for approval dialog
        app = flow_page.locator("button:has-text('Always approve'), button:has-text('Approve')").last
        if await app.count() > 0 and await app.is_visible():
            print("Found approval button:", await app.inner_text())
            await app.click()
            await flow_page.wait_for_timeout(2000)
            
        await flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\flow_part1_sent.png")
        print("Saved after send screenshot!")

if __name__ == "__main__":
    asyncio.run(send())
