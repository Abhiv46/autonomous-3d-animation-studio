import asyncio
import json
import urllib.request
import websockets

async def get_url():
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read())
    first_tab = tabs[0]
    ws_url = first_tab["webSocketDebuggerUrl"]
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        msg_id = 1
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cid = msg_id
            await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get("id") == cid:
                    return resp.get("result", {})

        js = """
        (() => {
            const closeBtn = document.querySelector("ytcp-button#close-button, button[aria-label*='Close' i]");
            if (closeBtn) closeBtn.click();
            const row = document.querySelector("ytcp-video-row");
            const link = row ? row.querySelector("a#video-title") : null;
            return link ? link.href : null;
        })()
        """
        res = await call("Runtime.evaluate", {"expression": js, "returnByValue": True})
        print("Video Row Link:", res.get("result", {}).get("value"))

if __name__ == "__main__":
    asyncio.run(get_url())
