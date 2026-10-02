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

        # Dismiss any open modal first
        await call('Runtime.evaluate', {
            'expression': "(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()"
        })
        await asyncio.sleep(1)

        # Find the card with '2a834cb3' and click its play button or card
        click_res = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const img = Array.from(document.querySelectorAll('img')).find(i => i.src && i.src.includes('2a834cb3'));
                if (!img) return 'img_not_found';
                const card = img.closest('[class*="card"], [class*="item"], [role="article"], div');
                const playBtn = card ? card.querySelector('button, [aria-label*="play" i], mat-icon') : null;
                if (playBtn) {
                    playBtn.click();
                    return 'clicked_play_btn';
                }
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
        print('Click result:', click_res.get('result', {}).get('value'))
        await asyncio.sleep(2.5)

        # Inspect videos in DOM
        vids = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const videos = Array.from(document.querySelectorAll('video')).map(v => ({
                    src: v.src,
                    currentSrc: v.currentSrc,
                    duration: v.duration,
                    w: v.videoWidth,
                    h: v.videoHeight
                }));
                const downloadBtn = Array.from(document.querySelectorAll('button, a')).find(b => 
                    (b.innerText && b.innerText.includes('download')) || 
                    b.getAttribute('aria-label') === 'Download' ||
                    (b.title && b.title.includes('Download'))
                );
                return {
                    videos: videos,
                    dlBtnFound: !!downloadBtn,
                    dlHref: downloadBtn ? downloadBtn.href : null
                };
            })()
            """,
            'returnByValue': True
        })
        print('Video info in DOM:', json.dumps(vids.get('result', {}).get('value'), indent=2))

if __name__ == '__main__':
    asyncio.run(check())
