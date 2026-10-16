import asyncio
import json
import urllib.request
import websockets

async def get_prompts():
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read())
    flow_tab = next((t for t in tabs if "3782c658" in t.get("url", "")), None)
    if not flow_tab:
        print("Flow tab not found")
        return
    ws_url = flow_tab["webSocketDebuggerUrl"]
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
            const els = Array.from(document.querySelectorAll("p, span, div, textarea"));
            const texts = els.map(e => (e.innerText || e.value || "").trim())
                             .filter(t => t.length > 20 && (t.toLowerCase().includes("mummy") || t.toLowerCase().includes("bandar") || t.toLowerCase().includes("monkey")));
            return Array.from(new Set(texts)).slice(0, 15);
        })()
        """
        res = await call("Runtime.evaluate", {"expression": js, "returnByValue": True})
        print(res.get("result", {}).get("value"))

if __name__ == "__main__":
    asyncio.run(get_prompts())
