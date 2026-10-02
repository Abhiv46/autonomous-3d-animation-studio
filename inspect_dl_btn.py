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

        btn_info = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const downloadBtn = Array.from(document.querySelectorAll('button, a')).find(b => 
                    (b.innerText && b.innerText.includes('download')) || 
                    b.getAttribute('aria-label') === 'Download' ||
                    (b.title && b.title.includes('Download'))
                );
                if (!downloadBtn) return 'none';
                return {
                    tag: downloadBtn.tagName,
                    href: downloadBtn.href,
                    outerHTML: downloadBtn.outerHTML.slice(0, 300)
                };
            })()
            """,
            'returnByValue': True
        })
        print('Download Button Info:', json.dumps(btn_info.get('result', {}).get('value'), indent=2))

if __name__ == '__main__':
    asyncio.run(check())
