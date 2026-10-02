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
                    const btns = Array.from(document.querySelectorAll('button, span, div'));
                    const always = btns.find(b => b.innerText && b.innerText.includes('Always approve'));
                    if (always && always.offsetParent !== null) {
                        always.click();
                        return { action: 'clicked_always_approve' };
                    }
                    const approve = btns.find(b => b.innerText && b.innerText.trim() === 'Approve');
                    if (approve && approve.offsetParent !== null) {
                        approve.click();
                        return { action: 'clicked_approve' };
                    }
                    const spinners = Array.from(document.querySelectorAll('[role="progressbar"], [class*="progress"], [class*="spin"], [class*="loading"]')).map(e => e.className);
                    const pm = document.querySelector('div.ProseMirror');
                    return {
                        action: 'none',
                        spinners: spinners,
                        pm_text_len: pm ? pm.innerText.trim().length : 0
                    };
                })()
                """,
                'returnByValue': True
            }
        }))
        res = json.loads(await ws.recv())
        print('Post trigger status:', json.dumps(res['result']['result']['value'], indent=2, ensure_ascii=True))

if __name__ == '__main__':
    asyncio.run(check())
