import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = [pg for pg in b.contexts[0].pages if "studio.youtube.com" in pg.url][0]
        await page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_kite_live_proof_final.png"
        await page.screenshot(path=proof_path)
        print("Screenshot saved to", proof_path)
        
        rows = await page.locator("ytcp-video-row").all()
        for i, r in enumerate(rows[:5]):
            t_loc = r.locator("#video-title")
            v_loc = r.locator(".table-cell.visibility, #visibility-cell")
            t = await t_loc.inner_text() if await t_loc.count() > 0 else "N/A"
            v = await v_loc.inner_text() if await v_loc.count() > 0 else "N/A"
            
            # get anchor link if any
            a_loc = r.locator("a#thumbnail-anchor, a[href*='/video/']").first
            href = await a_loc.get_attribute("href") if await a_loc.count() > 0 else ""
            print(f"Row {i+1}: Title=\"{t}\" | Visibility=\"{v}\" | Link=\"{href}\"")

if __name__ == "__main__":
    asyncio.run(check())
