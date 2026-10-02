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
                const main = document.querySelector('main') || document.body;
                const imgs = Array.from(main.querySelectorAll('img'));
                return imgs.map((img, i) => {
                    let parent = img.parentElement;
                    while (parent && !parent.className.includes('item') && !parent.className.includes('card') && parent.tagName !== 'FLOW-ASSET-CARD') {
                        if (parent === main) break;
                        parent = parent.parentElement;
                    }
                    return {
                        i,
                        src: img.src.slice(0, 60),
                        parentTag: parent ? parent.tagName : null,
                        parentClass: parent ? parent.className : null,
                        parentText: parent ? parent.innerText.slice(0, 80).replace(/\\n/g, ' ') : null
                    };
                });
            })()
            """,
            'returnByValue': True
        }}
        await ws.send(json.dumps(msg))
        res = json.loads(await ws.recv())
        print(json.dumps(res.get('result', {}).get('result', {}).get('value', []), indent=2))

if __name__ == '__main__':
    asyncio.run(inspect())
