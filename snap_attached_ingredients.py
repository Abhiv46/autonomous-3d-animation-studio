import asyncio
import json
import base64
import urllib.request
import websockets

async def check():
    req = urllib.request.urlopen('http://127.0.0.1:9222/json/list')
    tabs = json.loads(req.read().decode())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        msg_id = 1
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({'id': msg_id, 'method': method, 'params': params or {}}))
            while True:
                res = json.loads(await ws.recv())
                if res.get('id') == msg_id:
                    return res.get('result', {})

        await call('Page.enable')
        ss = await call('Page.captureScreenshot', {'format': 'png'})
        if 'data' in ss:
            with open(r'C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\attached_ingredients_live.png', 'wb') as f:
                f.write(base64.b64decode(ss['data']))
            print('Screenshot saved successfully!')

if __name__ == '__main__':
    asyncio.run(check())
