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

        top_btns = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const btns = Array.from(document.querySelectorAll('header button, [class*="header"] button, [class*="top"] button, [class*="nav"] button, button:has(mat-icon)'))
                    .map(b => ({
                        text: b.innerText ? b.innerText.trim() : '',
                        aria: b.getAttribute('aria-label') || ''
                    }))
                    .filter(x => x.text || x.aria);
                return btns.slice(0, 20);
            })()
            """,
            'returnByValue': True
        })
        print('Top Nav Buttons:', json.dumps(top_btns.get('result', {}).get('value'), indent=2))

if __name__ == '__main__':
    asyncio.run(check())
