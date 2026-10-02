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

        # Click download button
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const btn = Array.from(document.querySelectorAll('button')).find(b => 
                    (b.innerText && b.innerText.includes('download')) || 
                    b.getAttribute('aria-label') === 'Download'
                );
                if (btn) btn.click();
            })()
            """
        })
        await asyncio.sleep(1.5)

        # Inspect menu options
        options = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const items = Array.from(document.querySelectorAll('cdk-overlay-container button, cdk-overlay-container a, [role="menuitem"]'))
                    .map(el => ({
                        tag: el.tagName,
                        text: el.innerText ? el.innerText.trim() : '',
                        href: el.href || null
                    }));
                return items;
            })()
            """,
            'returnByValue': True
        })
        print('Download Menu Options:', json.dumps(options.get('result', {}).get('value'), indent=2))

if __name__ == '__main__':
    asyncio.run(check())
