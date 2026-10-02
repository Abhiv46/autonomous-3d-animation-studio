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
                    const modeBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Banana') || b.innerText.includes('Video') || b.innerText.includes('Image')));
                    const toasts = Array.from(document.querySelectorAll('[role="alert"], [class*="toast"], [class*="snack"], [class*="error"], [class*="notice"]')).map(e => e.innerText);
                    return {
                        modeBtnText: modeBtn ? modeBtn.innerText : 'not found',
                        promptAreaText: promptArea ? promptArea.innerText : 'not found',
                        toasts: toasts
                    };
                })()
                """,
                'returnByValue': True
            }
        }))
        res = json.loads(await ws.recv())
        print('Prompt Area Status:', json.dumps(res['result']['result']['value'], indent=2, ensure_ascii=True))

if __name__ == '__main__':
    asyncio.run(check())
