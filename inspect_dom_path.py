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

        dom_info = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const img = Array.from(document.querySelectorAll('img')).find(i => i.src && i.src.includes('d8622021'));
                if (!img) return 'not found';
                let el = img;
                const path = [];
                while (el && el !== document.body && path.length < 8) {
                    path.push({
                        tag: el.tagName,
                        className: el.className,
                        id: el.id
                    });
                    el = el.parentElement;
                }
                return path;
            })()
            """,
            'returnByValue': True
        })
        print('DOM Path above img:', json.dumps(dom_info.get('result', {}).get('value'), indent=2))

if __name__ == '__main__':
    asyncio.run(check())
