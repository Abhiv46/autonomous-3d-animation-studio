import asyncio
import json
import base64
from direct_cdp import DirectCDPClient, get_browser_ws

async def check():
    ws_url = await get_browser_ws()
    client = DirectCDPClient(ws_url)
    await client.connect()
    try:
        targets = await client.get_targets()
        session = None
        for t in targets:
            if "studio.youtube.com" in t.get("url", ""):
                session = await client.attach_to_target(t["targetId"])
                break
        if not session:
            print("No YT session")
            return
            
        await session.eval("""
        (() => {
            const closeBtn = document.querySelector("ytcp-button#close-button, button[aria-label*='Close' i]");
            if (closeBtn) closeBtn.click();
            window.location.href = 'https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short';
        })()
        """)
        await asyncio.sleep(6)
        
        info = await session.eval("""
        (() => {
            const rows = Array.from(document.querySelectorAll("ytcp-video-row"));
            return rows.slice(0, 5).map(r => {
                const title = r.querySelector("#video-title")?.innerText || '';
                const link = r.querySelector("a#thumbnail-anchor, a[href*='/video/']")?.href || '';
                const vis = r.querySelector(".table-cell.visibility, #visibility-cell")?.innerText || '';
                return { title, link, vis };
            });
        })()
        """)
        print("Recent Shorts:", json.dumps(info, indent=2))

        # Take screenshot of the shorts table
        res = await session.send("Page.captureScreenshot", {"format": "png"})
        with open(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_kite_shorts_channel_proof.png", "wb") as f:
            f.write(base64.b64decode(res["data"]))
        print("Proof screenshot saved!")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(check())
