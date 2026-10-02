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
        msg_id = 1
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({'id': msg_id, 'method': method, 'params': params or {}}))
            while True:
                res = json.loads(await ws.recv())
                if res.get('id') == msg_id:
                    return res.get('result', {})

        # Click settings trigger
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const btn = document.querySelector('button[aria-label="Settings trigger"], button.settings-trigger-button');
                if (btn) btn.click();
            })()
            """
        })
        await asyncio.sleep(1.5)
        
        # Check what options appear
        options = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const els = Array.from(document.querySelectorAll('cdk-overlay-container button, cdk-overlay-container [role="tab"], cdk-overlay-container span, [role="menu"] button'))
                    .map(b => b.innerText ? b.innerText.trim() : '')
                    .filter(t => t.length > 0 && t.length < 30);
                return Array.from(new Set(els));
            })()
            """,
            'returnByValue': True
        })
        print('Settings options in Image Editor:', json.dumps(options.get('result', {}).get('value'), indent=2))
        
        # Dismiss with Escape
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true });
                document.dispatchEvent(esc);
            })()
            """
        })

if __name__ == '__main__':
    asyncio.run(check())
