import asyncio
import json
from direct_cdp import DirectCDPClient, get_browser_ws

async def check_chat():
    ws_url = await get_browser_ws()
    client = DirectCDPClient(ws_url)
    await client.connect()
    try:
        targets = await client.get_targets()
        flow_target = next(t for t in targets if "flow.google.com/u/2" in t.get("url", ""))
        session = await client.attach_to_target(flow_target["targetId"])
        
        chat_text = await session.eval("""
        (() => {
            const drawer = document.querySelector('flow-side-sheet, [role="complementary"], .storyboard-studio') || document.body;
            return drawer.innerText.slice(-2000);
        })()
        """)
        print("Latest chat text:\n", chat_text)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(check_chat())
