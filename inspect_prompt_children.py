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
                    const promptArea = document.querySelector('.prompt-box, [class*="prompt-box"], div:has(> textarea)');
                    if (!promptArea) return 'no prompt area';
                    const children = Array.from(promptArea.querySelectorAll('*')).map(el => ({
                        tag: el.tagName,
                        className: el.className,
                        text: el.innerText ? el.innerText.trim().slice(0, 50) : '',
                        isContentEditable: el.isContentEditable,
                        value: el.value !== undefined ? el.value.slice(0, 50) : undefined
                    })).filter(x => x.text || x.value);
                    return children;
                })()
                """,
                'returnByValue': True
            }
        }))
        res = json.loads(await ws.recv())
        print('Prompt Area Children:', json.dumps(res['result']['result']['value'], indent=2, ensure_ascii=True))

if __name__ == '__main__':
    asyncio.run(check())
