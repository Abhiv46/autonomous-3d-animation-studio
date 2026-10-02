import asyncio
import json
import urllib.request
import websockets

async def check():
    req = urllib.request.urlopen('http://127.0.0.1:9222/json/list')
    tabs = json.loads(req.read().decode())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    async with websockets.connect(ws_url) as ws:
        msg_id = 1
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({'id': msg_id, 'method': method, 'params': params or {}}))
            while True:
                res = json.loads(await ws.recv())
                if res.get('id') == msg_id:
                    return res.get('result', {})

        # Get rect of generate button
        rect_res = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const btn = document.querySelector('button.generate-icon-button, [aria-label="Start generation"]');
                if (!btn) return null;
                const r = btn.getBoundingClientRect();
                return { x: r.left + r.width / 2, y: r.top + r.height / 2, w: r.width, h: r.height };
            })()
            """,
            'returnByValue': True
        })
        rect = rect_res.get('result', {}).get('value')
        print(f"Generate button center: {rect}", flush=True)
        if not rect:
            return

        cx, cy = int(rect['x']), int(rect['y'])
        
        # Real CDP Mouse Click
        await call('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': cx, 'y': cy})
        await asyncio.sleep(0.1)
        await call('Input.dispatchMouseEvent', {'type': 'mousePressed', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
        await asyncio.sleep(0.1)
        await call('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
        print(f"Dispatched real mouse click at ({cx}, {cy})!", flush=True)

if __name__ == '__main__':
    asyncio.run(check())
