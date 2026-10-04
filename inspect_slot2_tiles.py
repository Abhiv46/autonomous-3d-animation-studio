import asyncio
import json
from direct_cdp import DirectCDPClient, get_browser_ws

async def inspect_cards():
    ws_url = await get_browser_ws()
    client = DirectCDPClient(ws_url)
    await client.connect()
    try:
        targets = await client.get_targets()
        flow_target = next(t for t in targets if "flow.google.com/u/2" in t.get("url", ""))
        session = await client.attach_to_target(flow_target["targetId"])
        
        cards = await session.eval("""
        (() => {
            try {
                const els = document.querySelectorAll('*');
                let count = 0;
                for (let el of els) {
                    if (el.tagName.toLowerCase().includes('tile') || el.className.includes('tile') || el.className.includes('card')) {
                        count++;
                    }
                }
                return { count, totalElements: els.length };
            } catch(e) {
                return { error: e.message };
            }
        })()
        """)
        print("DOM summary:", cards)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(inspect_cards())
