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
                    const vids = Array.from(document.querySelectorAll("video")).map(v => ({ src: v.src, currentSrc: v.currentSrc }));
                    const promptBox = document.querySelector("[contenteditable='true'], textarea, div.ProseMirror");
                    const btns = Array.from(document.querySelectorAll("button")).map(b => b.innerText ? b.innerText.trim() : "").filter(x => x.length > 0);
                    return {
                        vids,
                        hasPromptBox: !!promptBox,
                        btns: btns.slice(0, 15)
                    };
                })()
                """)
                print("Canvas inspection:", json.dumps(data, indent=2))
                break
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run())
