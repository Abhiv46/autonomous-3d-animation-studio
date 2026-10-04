import asyncio
import json
from playwright.async_api import async_playwright

with open(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\prompts_18_parts.json", "r", encoding="utf-8") as f:
    prompts = json.load(f)

part_1 = prompts["part_1"]["prompt"]

async def test_dispatch():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        flow_page = [pg for pg in b.contexts[0].pages if "flow.google.com/u/2" in pg.url][0]
        await flow_page.bring_to_front()
        
        print("[1] Locating ProseMirror prompt box...", flush=True)
        pm = flow_page.locator("div.ProseMirror").first
        await pm.click()
        await flow_page.wait_for_timeout(300)
        await flow_page.keyboard.press("Control+A")
        await flow_page.keyboard.press("Backspace")
        
        print("[2] Typing Part 1 prompt...", flush=True)
        await flow_page.keyboard.type(part_1, delay=2)
        await flow_page.wait_for_timeout(1000)
        
        # Check start generation button
        send_btn = flow_page.locator("button[aria-label*='Start generation' i], button:has-text('arrow_forward')").last
        is_disabled = await send_btn.is_disabled()
        print(f"[3] Send button found. Disabled: {is_disabled}", flush=True)
        
        await flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\flow_part1_typed.png")
        print("Screenshot of typed prompt saved!")

if __name__ == "__main__":
    asyncio.run(test_dispatch())
