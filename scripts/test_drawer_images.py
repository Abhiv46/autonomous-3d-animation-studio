import asyncio
import json
import urllib.request
import websockets

async def check_drawer_images():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/list').read())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        msg_id = 0
        async def send(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cur_id = msg_id
            await ws.send(json.dumps({'id': cur_id, 'method': method, 'params': params or {}}))
            while True:
                res = json.loads(await ws.recv())
                if res.get('id') == cur_id:
                    return res.get('result', {})

        # Click '+' button in prompt box
        print('Clicking + button...')
        await send('Runtime.evaluate', {
            'expression': """
            (() => {
                const addBtn = Array.from(document.querySelectorAll('button')).find(b => 
                    b.getAttribute('aria-label') === 'Add ingredients to the prompt box' ||
                    (b.innerText && b.innerText.trim() === 'add' && b.closest('.prompt-box, flow-base-prompt-box'))
                );
                if (addBtn) addBtn.click();
            })()
            """
        })
        await asyncio.sleep(2)

        # Click Images tab in drawer
        print('Clicking Images tab...')
        await send('Runtime.evaluate', {
            'expression': """
            (() => {
                const tabs = Array.from(document.querySelectorAll('mat-list-item, [role="tab"], button, span, div'));
                const imgTab = tabs.find(t => t.innerText && t.innerText.trim() === 'Images');
                if (imgTab) imgTab.click();
            })()
            """
        })
        await asyncio.sleep(2)

        # Inspect items
        res = await send('Runtime.evaluate', {
            'expression': """
            (() => {
                const items = Array.from(document.querySelectorAll('.asset-item, flow-add-menu-asset-item, [role="option"]'));
                return items.map((i, idx) => ({
                    idx,
                    text: i.innerText ? i.innerText.trim().replace(/\\n/g, ' | ') : '',
                    tag: i.tagName
                })).slice(0, 10);
            })()
            """,
            'returnByValue': True
        })
        print('Drawer image items:', json.dumps(res.get('result', {}).get('value', []), indent=2))

if __name__ == '__main__':
    asyncio.run(check_drawer_images())
