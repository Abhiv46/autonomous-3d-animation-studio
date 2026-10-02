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
                await session.eval("""
                (() => {
                    const closeBtn = document.querySelector("button[aria-label='Close'], .close-button, [aria-label*='close' i]");
                    if (closeBtn) closeBtn.click();
                    const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true });
                    document.dispatchEvent(esc);
                })()
                """)
                await asyncio.sleep(1)
                break
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run())
