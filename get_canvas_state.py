import asyncio
import json
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
                data = await session.eval("""
                (() => {
                    const cards = Array.from(document.querySelectorAll("[class*='tile'], [class*='card'], [role='button']"))
                        .map(el => el.innerText.trim())
                        .filter(t => t.length > 0 && t.length < 60);
                    const promptBox = document.querySelector("[contenteditable='true'], textarea, div.ProseMirror");
                    const statusText = document.body.innerText.slice(-600);
                    return {
                        cards: Array.from(new Set(cards)).slice(0, 10),
                        hasPromptBox: !!promptBox,
                        statusSummary: statusText.replace(/\\n+/g, ' ')
                    };
                })()
                """)
                print("Canvas live state:", json.dumps(data, indent=2))
                break
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run())
