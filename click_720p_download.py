import asyncio
import json
import urllib.request
import websockets

async def check():
    req = urllib.request.urlopen('http://127.0.0.1:9222/json/list')
    tabs = json.loads(req.read().decode())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        msg_id = 1
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({'id': msg_id, 'method': method, 'params': params or {}}))
            while True:
                res = json.loads(await ws.recv())
                if res.get('id') == msg_id:
                    return res.get('result', {})

        # Click the 720p option in download menu
        res = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const btns = Array.from(document.querySelectorAll('cdk-overlay-container button, [role="menuitem"]'));
                const btn720 = btns.find(b => b.innerText && b.innerText.includes('720p'));
                if (btn720) {
                    btn720.click();
                    return 'clicked_720p';
                }
                return 'not_found';
            })()
            """,
            'returnByValue': True
        })
        print('Click 720p result:', res.get('result', {}).get('value'))
        await asyncio.sleep(3)

        # Dismiss modal
        await call('Runtime.evaluate', {
            'expression': "(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()"
        })

if __name__ == '__main__':
    asyncio.run(check())
