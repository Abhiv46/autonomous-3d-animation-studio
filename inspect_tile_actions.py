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

        # Find the image tile on canvas and inspect all its buttons & actions
        tile_info = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const img = Array.from(document.querySelectorAll('img')).find(i => i.src && i.src.includes('d8622021'));
                if (!img) return 'img not found';
                const tile = img.closest('[class*="card"], [class*="item"], [class*="tile"], div:has(> img)');
                if (!tile) return 'tile not found';
                const btns = Array.from(tile.querySelectorAll('button, a, [role="button"]')).map(b => ({
                    text: b.innerText ? b.innerText.trim() : '',
                    aria: b.getAttribute('aria-label') || '',
                    title: b.getAttribute('title') || ''
                }));
                return {
                    tileText: tile.innerText,
                    buttons: btns
                };
            })()
            """,
            'returnByValue': True
        })
        print('Tile info:', json.dumps(tile_info.get('result', {}).get('value'), indent=2))

if __name__ == '__main__':
    asyncio.run(check())
