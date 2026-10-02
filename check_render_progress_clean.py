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
        await ws.send(json.dumps({
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """
                (() => {
                    const progress = Array.from(document.querySelectorAll('.loading-percentage, [class*="progress"], [class*="percent"], [class*="status"]'))
                        .map(e => e.innerText ? e.innerText.trim() : '')
                        .filter(t => t.length > 0 && t.length < 30);
                    const spinners = document.querySelectorAll('.loading-percentage').length;
                    return { progress: progress, spinners: spinners };
                })()
                """,
                'returnByValue': True
            }
        }))
        res = json.loads(await ws.recv())
        print('Live Render Status:', json.dumps(res['result']['result']['value'], indent=2, ensure_ascii=True))

if __name__ == '__main__':
    asyncio.run(check())
