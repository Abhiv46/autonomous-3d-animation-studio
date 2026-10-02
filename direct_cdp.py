import asyncio
import json
import base64
import urllib.request
import websockets

class DirectCDPClient:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self._msg_id = 0
        self._futures = {}
        self._listen_task = None

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, max_size=50*1024*1024, ping_interval=None)
        self._listen_task = asyncio.create_task(self._reader())

    async def _reader(self):
        try:
            while True:
                raw = await self.ws.recv()
                data = json.loads(raw)
                msg_id = data.get("id")
                if msg_id is not None and msg_id in self._futures:
                    fut = self._futures.pop(msg_id)
                    if not fut.done():
                        if "error" in data:
                            fut.set_exception(Exception(f"CDP Error: {data['error']}"))
                        else:
                            fut.set_result(data.get("result", {}))
        except asyncio.CancelledError:
            pass
        except Exception as e:
            for fut in self._futures.values():
                if not fut.done():
                    fut.set_exception(e)

    async def close(self):
        if self._listen_task:
            self._listen_task.cancel()
        if self.ws:
            await self.ws.close()

    async def send(self, method, params=None, session_id=None):
        self._msg_id += 1
        cur_id = self._msg_id
        fut = asyncio.get_running_loop().create_future()
        self._futures[cur_id] = fut
        
        payload = {"id": cur_id, "method": method, "params": params or {}}
        if session_id:
            payload["sessionId"] = session_id
            
        await self.ws.send(json.dumps(payload))
        return await asyncio.wait_for(fut, timeout=20)

    async def get_targets(self):
        res = await self.send("Target.getTargets")
        return res.get("targetInfos", [])

    async def create_target(self, url):
        res = await self.send("Target.createTarget", {"url": url})
        return res.get("targetId")

    async def attach_to_target(self, target_id):
        res = await self.send("Target.attachToTarget", {"targetId": target_id, "flatten": True})
        session_id = res.get("sessionId")
        session = DirectSession(self, session_id)
        return session

class DirectSession:
    def __init__(self, client, session_id):
        self.client = client
        self.session_id = session_id

    async def send(self, method, params=None):
        return await self.client.send(method, params, self.session_id)

    async def eval(self, js):
        res = await self.send("Runtime.evaluate", {
            "expression": js,
            "returnByValue": True,
            "awaitPromise": True
        })
        return res.get("result", {}).get("value")

    async def screenshot(self, file_path):
        res = await self.send("Page.captureScreenshot", {"format": "png"})
        img_bytes = base64.b64decode(res["data"])
        with open(file_path, "wb") as f:
            f.write(img_bytes)
        print(f"[+] Saved screenshot to: {file_path}", flush=True)

    async def navigate(self, url):
        return await self.send("Page.navigate", {"url": url})

async def get_browser_ws():
    res = urllib.request.urlopen("http://127.0.0.1:9222/json/version")
    data = json.loads(res.read().decode())
    return data["webSocketDebuggerUrl"]
