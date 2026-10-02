import urllib.request, json, asyncio, websockets

async def check_chars():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/list').read())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        msg_id = 0
        async def send(method, params=None):
            nonlocal msg_id
            msg_id += 1
            msg = {'id': msg_id, 'method': method, 'params': params or {}}
            await ws.send(json.dumps(msg))
            while True:
                res = json.loads(await ws.recv())
                if res.get('id') == msg_id:
                    return res.get('result', {})

        # Click Characters tab
        print('Clicking Characters...')
        res1 = await send('Runtime.evaluate', {
            'expression': """
            (() => {
                const tabs = Array.from(document.querySelectorAll('mat-list-item, [role="tab"], button, span, div'));
                const charTab = tabs.find(t => t.innerText && t.innerText.trim() === 'Characters');
                if (charTab) { charTab.click(); return 'clicked characters'; }
                return 'not found';
            })()
            """,
            'returnByValue': True
        })
        print('Tab click:', res1.get('result', {}).get('value'))
        await asyncio.sleep(2)

        # List items in drawer
        res = await send('Runtime.evaluate', {
            'expression': """
            (() => {
                const els = Array.from(document.querySelectorAll('*'));
                const targets = els.filter(e => e.innerText && (e.innerText.includes('Kaavya') || e.innerText.includes('Kaartik') || e.innerText.includes('Pinki'))).map(e => ({tag: e.tagName, text: e.innerText.trim(), class: e.className}));
                return targets;
            })()
            """,
            'returnByValue': True
        })
        print('Items visible:', json.dumps(res.get('result', {}).get('value', []), indent=2))

if __name__ == '__main__':
    asyncio.run(check_chars())
