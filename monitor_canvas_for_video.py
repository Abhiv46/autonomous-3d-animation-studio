import asyncio
import json
import urllib.request
import os
import websockets

RAW_CLIPS_DIR = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips"

async def check():
    req = urllib.request.urlopen('http://127.0.0.1:9222/json/list')
    tabs = json.loads(req.read().decode())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    print(f"Connecting to tab WS: {ws_url}", flush=True)
    
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

        for attempt in range(40):
            await asyncio.sleep(5)
            # Check for approvals
            app = await call('Runtime.evaluate', {
                'expression': """
                (() => {
                    const always = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Always approve'));
                    if (always && always.offsetParent !== null) { always.click(); return 'always_approved'; }
                    const approve = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.trim() === 'Approve');
                    if (approve && approve.offsetParent !== null) { approve.click(); return 'approved'; }
                    return 'none';
                })()
                """,
                'returnByValue': True
            })
            val = app.get('result', {}).get('value')
            if val in ['always_approved', 'approved']:
                print(f"Clicked approval: {val}", flush=True)

            # Check percentage
            p_res = await call('Runtime.evaluate', {
                'expression': """
                (() => {
                    const p = Array.from(document.querySelectorAll('.loading-percentage, [class*="progress"], [class*="percent"]')).map(e => e.innerText ? e.innerText.trim() : '');
                    const stopBtn = !!document.querySelector('flow-stop-icon-button, button.stop-button');
                    return { p, stopBtn };
                })()
                """,
                'returnByValue': True
            })
            info = p_res.get('result', {}).get('value', {})
            p_list = info.get('p', [])
            stop_btn = info.get('stopBtn', False)
            if p_list:
                print(f"Progress: {p_list[0]}", flush=True)
            elif stop_btn:
                print("Creative agent actively processing...", flush=True)
            else:
                print("Generation complete or stopped! Checking video cards...", flush=True)
                break

        # Check latest video card and download
        await asyncio.sleep(2)
        click_card = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const imgs = Array.from(document.querySelectorAll('img')).filter(i => i.src && i.src.includes('flow-content.google/image'));
                if (imgs.length > 0) {
                    const card = imgs[0].closest('[class*="card"], [class*="item"], div:has(> img)');
                    if (card) { card.click(); return 'clicked'; }
                }
                return 'not_found';
            })()
            """,
            'returnByValue': True
        })
        print(f"Card click: {click_card.get('result', {}).get('value')}", flush=True)
        await asyncio.sleep(2)

        media = await call('Runtime.evaluate', {
            'expression': "document.querySelector('video') ? document.querySelector('video').src : null",
            'returnByValue': True
        })
        vid_url = media.get('result', {}).get('value')
        print(f"Harvested Video URL: {vid_url}", flush=True)

        if vid_url:
            out_file = os.path.join(RAW_CLIPS_DIR, "ep22_scene2.mp4")
            urllib.request.urlretrieve(vid_url, out_file)
            print(f"[SUCCESS] Scene 2 MP4 downloaded: {out_file} ({os.path.getsize(out_file)} bytes)", flush=True)

        # Close video modal
        await call('Runtime.evaluate', {
            'expression': "(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()"
        })

if __name__ == '__main__':
    asyncio.run(check())
