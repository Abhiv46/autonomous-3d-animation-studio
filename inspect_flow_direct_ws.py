import asyncio
import json
import urllib.request
import websockets

async def check():
    req = urllib.request.urlopen('http://127.0.0.1:9222/json/list')
    tabs = json.loads(req.read().decode())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    print(f"Connecting to tab WS: {ws_url}", flush=True)
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        msg_id = 1
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({'id': msg_id, 'method': method, 'params': params or {}}))
            while True:
                res = json.loads(await ws.recv())
                if res.get('id') == msg_id:
                    return res
        
        info = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                return {
                    title: document.title,
                    url: window.location.href,
                    textarea: document.querySelector('textarea') ? document.querySelector('textarea').value : null,
                    buttons: Array.from(document.querySelectorAll('button')).map(b => b.innerText ? b.innerText.trim() : '').filter(t => t.length > 0).slice(0, 15)
                };
            })()
            """,
            'returnByValue': True
        })
        print('Flow Tab Info:', json.dumps(info.get('value'), indent=2, ensure_ascii=True))

if __name__ == "__main__":
    asyncio.run(check())
