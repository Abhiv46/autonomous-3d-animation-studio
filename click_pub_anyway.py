import asyncio
import json
import base64
import urllib.request
import websockets

async def click_pub_anyway():
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read())
    yt_tab = next(t for t in tabs if "studio.youtube.com" in t.get("url", "").lower())
    ws_url = yt_tab["webSocketDebuggerUrl"]
    async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
        msg_id = 0
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cid = msg_id
            await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get("id") == cid: return resp.get("result", {})

        res = await call("Runtime.evaluate", {
            "expression": """
            (() => {
                const btns = Array.from(document.querySelectorAll("button, ytcp-button"));
                const btn = btns.find(b => b.innerText && b.innerText.includes('Publish anyway'));
                if (btn) {
                    btn.click();
                    return 'clicked';
                }
                return 'not_found';
            })()
            """,
            "returnByValue": True,
            "awaitPromise": True
        })
        print("Publish anyway click:", res.get("result", {}).get("value"))
        await asyncio.sleep(4)

        # Close any dialog if present
        await call("Runtime.evaluate", {
            "expression": """
            (() => {
                const closeBtn = document.querySelector("ytcp-button#close-button, button[aria-label*='Close' i]");
                if (closeBtn) closeBtn.click();
            })()
            """
        })
        await asyncio.sleep(3)

        # Navigate to Shorts list
        await call("Page.navigate", {"url": "https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short"})
        await asyncio.sleep(6)

        # Take screenshot
        await call("Page.enable")
        s_res = await call("Page.captureScreenshot", {"format": "png"})
        proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_color_public_verified.png"
        with open(proof, "wb") as f:
            f.write(base64.b64decode(s_res["data"]))
        print("Verified screenshot saved to", proof)

if __name__ == "__main__":
    asyncio.run(click_pub_anyway())
