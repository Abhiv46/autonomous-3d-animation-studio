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

        # Click the image card in the overlay picker
        click_img = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const img = document.querySelector('cdk-overlay-container img, [class*="overlay"] img, [class*="grid"] img');
                if (img) {
                    const card = img.closest('[class*="item"], [class*="tile"], button, div');
                    if (card) {
                        card.click();
                        return 'card_clicked';
                    }
                    img.click();
                    return 'img_clicked';
                }
                return 'img_not_found';
            })()
            """,
            'returnByValue': True
        })
        print('Click Image Result:', click_img.get('result', {}).get('value'))
        await asyncio.sleep(2)
        
        # Check prompt box to see if ingredient pill is attached!
        pills = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const promptBox = document.querySelector('.prompt-box, [class*="prompt-box"], flow-base-prompt-box');
                const attachedImgs = promptBox ? Array.from(promptBox.querySelectorAll('img')).map(i => ({ src: i.src.slice(0, 50), w: i.width, h: i.height })) : [];
                const pills = promptBox ? Array.from(promptBox.querySelectorAll('[class*="chip"], [class*="pill"], [class*="badge"], [class*="tag"]')).map(p => p.innerText) : [];
                return { attachedImgs, pills, text: promptBox ? promptBox.innerText.slice(0, 100) : '' };
            })()
            """,
            'returnByValue': True
        })
        print('Attached Ingredients in Prompt Box:', json.dumps(pills.get('result', {}).get('value'), indent=2))

if __name__ == '__main__':
    asyncio.run(check())
