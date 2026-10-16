import asyncio
import json
import urllib.request
import websockets
import base64

async def finalize_yt():
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

        async def eval_js(js):
            res = await call("Runtime.evaluate", {"expression": js, "returnByValue": True, "awaitPromise": True})
            return res.get("result", {}).get("value")

        # 1. Click Publish button
        js_click = """
        (() => {
            const btns = Array.from(document.querySelectorAll("button, ytcp-button"));
            const pubBtn = btns.find(b => b.innerText && b.innerText.trim().toLowerCase() === 'publish' || b.id === 'done-button');
            if (pubBtn) {
                pubBtn.click();
                return 'publish_clicked';
            }
            return 'not_found';
        })()
        """
        res = await eval_js(js_click)
        print("Publish button click result:", res)
        await asyncio.sleep(6)

        # 2. Check for dialog or close button
        js_info = """
        (() => {
            const links = Array.from(document.querySelectorAll("a"))
                .map(a => a.href)
                .filter(h => h.includes("youtu.be") || h.includes("shorts"));
            const closeBtn = document.querySelector("ytcp-button#close-button, button[aria-label*='Close' i]");
            if (closeBtn) closeBtn.click();
            return { links: links };
        })()
        """
        info = await eval_js(js_info)
        print("Published info:", info)
        await asyncio.sleep(2)

        # 3. Take screenshot
        await call("Page.enable")
        s_res = await call("Page.captureScreenshot", {"format": "png"})
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_jhumka_final_published.png"
        with open(proof_path, "wb") as f:
            f.write(base64.b64decode(s_res["data"]))
        print("Final screenshot saved to:", proof_path)

if __name__ == "__main__":
    asyncio.run(finalize_yt())
