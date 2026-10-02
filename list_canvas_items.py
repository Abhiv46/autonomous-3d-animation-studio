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
                    const imgs = Array.from(document.querySelectorAll('img')).map(i => {
                        let parent = i.closest('[class*="card"], [class*="item"], [role="article"], div');
                        return {
                            src: i.src,
                            w: i.width,
                            h: i.height,
                            alt: i.alt || '',
                            parent_text: parent && parent.innerText ? parent.innerText.slice(0, 80).replace(/\\n/g, ' ') : ''
                        };
                    });
                    return imgs;
                })()
                """,
                'returnByValue': True
            }
        }))
        res = json.loads(await ws.recv())
        print('Images:', json.dumps(res['result']['result']['value'], indent=2, ensure_ascii=True))

if __name__ == '__main__':
    asyncio.run(check())
