import asyncio
import json
import urllib.request
import websockets

async def get_yt_count():
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
            const rows = Array.from(document.querySelectorAll("ytcp-video-row"));
            return rows.slice(0, 8).map((r, idx) => {
                const title = r.querySelector("#video-title") ? r.querySelector("#video-title").innerText.trim() : "";
                const visibility = r.querySelector(".cell-body.table-body-cell-visibility") ? r.querySelector(".cell-body.table-body-cell-visibility").innerText.trim() : "";
                return { idx: idx + 1, title: title, visibility: visibility };
            });
        })()
        """
        res = await call("Runtime.evaluate", {"expression": js, "returnByValue": True})
        items = res.get("result", {}).get("value", [])
        print("=== RECENT YOUTUBE VIDEOS ===")
        for item in items:
            t = item["title"].encode("ascii", "ignore").decode()
            v = item["visibility"].encode("ascii", "ignore").decode()
            print(f"{item['idx']}. [{v}] {t}")

if __name__ == "__main__":
    asyncio.run(get_yt_count())
