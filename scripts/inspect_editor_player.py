import asyncio
import json
import urllib.request
import websockets

async def inspect():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/list').read())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        msg = {'id': 1, 'method': 'Runtime.evaluate', 'params': {
            'expression': """
            (() => {
                const els = Array.from(document.querySelectorAll('*'));
                const playerEl = els.find(e => e.className && typeof e.className === 'string' && e.className.includes('player'));
                return playerEl ? { tag: playerEl.tagName, class: playerEl.className, html: playerEl.innerHTML.slice(0, 500) } : 'none';
            })()
            """,
            'returnByValue': True
        }}
        await ws.send(json.dumps(msg))
        res = json.loads(await ws.recv())
        print(json.dumps(res.get('result', {}).get('result', {}).get('value', {}), indent=2))

if __name__ == '__main__':
    asyncio.run(inspect())
