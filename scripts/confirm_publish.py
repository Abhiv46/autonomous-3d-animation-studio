import asyncio
import json
import urllib.request
import websockets

async def click_publish_anyway():
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read())
    yt_tab = next((t for t in tabs if "studio.youtube.com" in t.get("url", "").lower()), None)
    ws_url = yt_tab["webSocketDebuggerUrl"]
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        msg_id = 200
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cid = msg_id
            await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get("id") == cid:
                    return resp.get("result", {})

        async def eval_js(js):
            res = await call("Runtime.evaluate", {"expression": js, "returnByValue": True, "awaitPromise": True})
            return res.get("result", {}).get("value")

        js_click = """
        (() => {
            const btns = Array.from(document.querySelectorAll("button, ytcp-button"));
            const pubAnyway = btns.find(b => b.innerText && b.innerText.trim().toLowerCase().includes("publish anyway"));
            if (pubAnyway) {
                pubAnyway.click();
                return "clicked_publish_anyway";
            }
            return "not_found";
        })()
        """
        res = await eval_js(js_click)
        print("Publish anyway click result:", res)
        await asyncio.sleep(4)
        
        js_close = """
        (() => {
            const closeBtn = document.querySelector("ytcp-button#close-button, button[aria-label*='Close' i]");
            if (closeBtn) {
                closeBtn.click();
                return "closed";
            }
            return "no_close";
        })()
        """
        res_close = await eval_js(js_close)
        print("Close modal result:", res_close)

if __name__ == "__main__":
    asyncio.run(click_publish_anyway())
