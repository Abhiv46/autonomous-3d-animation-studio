import asyncio
import json
import urllib.request
import websockets

async def inspect_cards():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/list').read())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        msg = {'id': 1, 'method': 'Runtime.evaluate', 'params': {
            'expression': """
            (() => {
                const cards = Array.from(document.querySelectorAll('flow-project-card, [class*="card"]')).filter(c => c.querySelector('img, video, [class*="failed"]'));
                return cards.map((c, idx) => ({
                    idx,
                    text: c.innerText ? c.innerText.trim().replace(/\\n/g, ' | ') : '',
                    hasVideo: !!c.querySelector('video, flow-video-player, [data-mat-icon-name="play_circle"]'),
                    buttons: Array.from(c.querySelectorAll('button')).map(b => b.innerText.trim() || b.getAttribute('aria-label'))
                })).slice(0, 10);
            })()
            """,
            'returnByValue': True
        }}
        await ws.send(json.dumps(msg))
        res = json.loads(await ws.recv())
        print(json.dumps(res.get('result', {}).get('result', {}).get('value', []), indent=2))

if __name__ == '__main__':
    asyncio.run(inspect_cards())
