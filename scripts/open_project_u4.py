import urllib.request, json, asyncio, websockets, time

async def main():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/list').read())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    print('Connecting to:', ws_url)
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

        # Find and click The Naughty Duo project
        expr = """
        (() => {
            const els = Array.from(document.querySelectorAll('.project-title-label'));
            const target = els.find(e => e.innerText && e.innerText.includes('The Naughty Duo'));
            if (!target) return 'target not found';
            
            // Look for closest card or clickable ancestor
            let p = target;
            while (p && p.tagName !== 'BODY') {
                if (p.getAttribute('role') === 'button' || (p.className && String(p.className).includes('card'))) {
                    p.click();
                    return 'Clicked ancestor: ' + p.tagName + ' / ' + p.className;
                }
                p = p.parentElement;
            }
            target.click();
            return 'Clicked target directly';
        })()
        """
        res = await send('Runtime.evaluate', {'expression': expr, 'returnByValue': True})
        print('Result:', res.get('result', {}).get('value'))
        
        await asyncio.sleep(4)
        url_res = await send('Runtime.evaluate', {'expression': 'window.location.href'})
        print('Current URL:', url_res.get('result', {}).get('value'))

if __name__ == '__main__':
    asyncio.run(main())
