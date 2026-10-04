import asyncio
import json
import base64
from direct_cdp import DirectCDPClient, get_browser_ws

async def check_studio():
    ws_url = await get_browser_ws()
    client = DirectCDPClient(ws_url)
    await client.connect()
    try:
        targets = await client.get_targets()
        yt_t = next(t for t in targets if "youtube.com" in t.get("url", ""))
        session = await client.attach_to_target(yt_t["targetId"])
        
        print("Navigating to studio.youtube.com...", flush=True)
        await session.eval("window.location.href = 'https://studio.youtube.com/'")
        await asyncio.sleep(5)
        
        info = await session.eval("""
        (() => {
            const channelName = document.querySelector('#channel-name, .channel-name, #entity-name')?.innerText || '';
            const currentUrl = window.location.href;
            const title = document.title;
            return { channelName, currentUrl, title };
        })()
        """)
        print("Studio Info:", info)
        
        res = await session.send("Page.captureScreenshot", {"format": "png"})
        proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\studio_check.png"
        with open(proof, "wb") as f:
            f.write(base64.b64decode(res["data"]))
        print("Saved proof to", proof)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(check_studio())
