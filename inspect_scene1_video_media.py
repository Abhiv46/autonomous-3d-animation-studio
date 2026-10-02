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

        # Click the new video card to inspect its video element or download button
        click_res = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const img = Array.from(document.querySelectorAll('img')).find(i => i.src && i.src.includes('1c934572'));
                if (!img) return 'not found';
                const card = img.closest('[class*="card"], [class*="item"], [role="article"], div:has(> img)');
                if (card) {
                    card.click();
                    return 'clicked_card';
                }
                img.click();
                return 'clicked_img';
            })()
            """,
            'returnByValue': True
        })
        print('Card Click Result:', click_res.get('result', {}).get('value'))
        await asyncio.sleep(2)

        # Check for video tag and download button
        media_info = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const video = document.querySelector('video');
                const dlBtn = Array.from(document.querySelectorAll('button, a')).find(b => 
                    (b.innerText && b.innerText.includes('download')) || 
                    b.getAttribute('aria-label') === 'Download' ||
                    (b.title && b.title.includes('Download'))
                );
                return {
                    videoSrc: video ? video.src : null,
                    downloadBtnFound: !!dlBtn,
                    downloadBtnHref: dlBtn ? dlBtn.href : null
                };
            })()
            """,
            'returnByValue': True
        })
        print('Media Info:', json.dumps(media_info.get('result', {}).get('value'), indent=2))

if __name__ == '__main__':
    asyncio.run(check())
