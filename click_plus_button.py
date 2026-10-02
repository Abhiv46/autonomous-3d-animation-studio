import asyncio
from direct_cdp import DirectCDPClient, get_browser_ws

async def run():
    ws_url = await get_browser_ws()
    client = DirectCDPClient(ws_url)
    await client.connect()
    try:
        targets = await client.get_targets()
        for t in targets:
            if t.get("type") == "page" and "flow.google.com" in t.get("url", ""):
                session = await client.attach_to_target(t["targetId"])
                
                # Click the '+' button in the prompt box
                res = await session.eval("""
                (() => {
                    const promptArea = document.querySelector(".prompt-box, [class*='prompt-box'], div:has(> [contenteditable='true'])");
                    const btns = Array.from(document.querySelectorAll("button"));
                    // The '+' button is usually inside or next to prompt box
                    const plusBtn = btns.find(b => b.innerText && b.innerText.trim() === 'add');
                    if (plusBtn) {
                        plusBtn.click();
                        return 'plus_clicked';
                    }
                    return 'plus_not_found';
                })()
                """)
                print("Click plus result:", res)
                await asyncio.sleep(1)
                
                # Inspect open overlay/menu
                menu_data = await session.eval("""
                (() => {
                    const els = Array.from(document.querySelectorAll("[role='menuitem'], [class*='item'], [class*='option'], button"))
                        .map(el => el.innerText ? el.innerText.trim() : '')
                        .filter(t => t.length > 0 && t.length < 50);
                    return Array.from(new Set(els));
                })()
                """)
                print("Open menu options:", menu_data[:20])
                await session.screenshot(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\plus_menu_open.png")
                break
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run())
