import asyncio
import json
from playwright.async_api import async_playwright

with open(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\prompts_18_parts.json", "r", encoding="utf-8") as f:
    prompts = json.load(f)

part_2_prompt = "Use Veo 3.1 - Lite (8 seconds is fine). Please generate this exact scene now for PART 2:\n" + prompts["part_2"]["prompt"]

async def send_part2():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        flow_page = [pg for pg in b.contexts[0].pages if "flow.google.com/u/2" in pg.url][0]
        
        await flow_page.evaluate("""(text) => {
            const pm = document.querySelector('div.ProseMirror');
            if (pm) {
                pm.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, text);
                pm.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }""", part_2_prompt)
        await flow_page.wait_for_timeout(1500)
        
        send_btn = flow_page.locator("button[aria-label*='Start generation' i], button:has-text('arrow_forward')").last
        print("Clicking Start Generation for Part 2...", flush=True)
        await send_btn.click(force=True)
        await flow_page.wait_for_timeout(4000)
        
        for _ in range(5):
            app = flow_page.locator("button:has-text('Always approve'), button:has-text('Approve')").last
            if await app.count() > 0 and await app.is_visible():
                print("Clicked approval:", await app.inner_text(), flush=True)
                await app.click(force=True)
                await flow_page.wait_for_timeout(1500)
                break
            await asyncio.sleep(1)

        print("Part 2 submitted successfully!")

if __name__ == "__main__":
    asyncio.run(send_part2())
