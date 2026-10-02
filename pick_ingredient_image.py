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

        # Click Images tab in ingredient menu
        click_res = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const items = Array.from(document.querySelectorAll('mat-list-item, [role="menuitem"], button, span'));
                const imgItem = items.find(i => i.innerText && i.innerText.includes('Images'));
                if (imgItem) {
                    imgItem.click();
                    return 'clicked_images_menu';
                }
                return 'images_menu_not_found';
            })()
            """,
            'returnByValue': True
        })
        print('Click Images menu:', click_res.get('result', {}).get('value'))
        await asyncio.sleep(2)
        
        # See what images appear to pick
        options = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const els = Array.from(document.querySelectorAll('cdk-overlay-container img, [class*="overlay"] img, [class*="grid"] img, [class*="picker"] img, [class*="drawer"] img, [role="dialog"] img, [class*="panel"] img'))
                    .map(i => ({ src: i.src.slice(0, 70), alt: i.alt || '', w: i.width, h: i.height }));
                return els;
            })()
            """,
            'returnByValue': True
        })
        print('Available images to pick:', json.dumps(options.get('result', {}).get('value'), indent=2))

if __name__ == '__main__':
    asyncio.run(check())
