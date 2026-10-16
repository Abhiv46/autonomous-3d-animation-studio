import asyncio
import json
import urllib.request
import websockets
import base64

async def check_details():
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read())
    edit_tab = next((t for t in tabs if "video/P3y5NiV-pG4/edit" in t.get("url", "")), None)
    if not edit_tab:
        print("Edit tab not found, looking for any studio tab...")
        edit_tab = next((t for t in tabs if "studio.youtube.com" in t.get("url", "")), None)
        
    ws_url = edit_tab["webSocketDebuggerUrl"]
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

        # Capture screenshot
        await call("Page.enable")
        s_res = await call("Page.captureScreenshot", {"format": "png"})
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_seo_check_details.png"
        with open(proof_path, "wb") as f:
            f.write(base64.b64decode(s_res["data"]))
        print("Screenshot saved to:", proof_path)
        
        js_extract = """
        (() => {
            const titleEl = document.querySelector("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox, #title-textarea #textbox");
            const descEl = document.querySelector("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox, #description-textarea #textbox");
            const chips = Array.from(document.querySelectorAll("ytcp-chip span.chip-text, #chip-text")).map(c => c.innerText.trim());
            return {
                title: titleEl ? titleEl.innerText.trim() : null,
                descLength: descEl ? descEl.innerText.length : 0,
                descSnippet: descEl ? descEl.innerText.substring(0, 150) : null,
                tags: chips
            };
        })()
        """
        info = await eval_js(js_extract)
        print("SEO Info on Page:", info)

if __name__ == "__main__":
    asyncio.run(check_details())
