import asyncio
import json
import urllib.request
import websockets
import time
from pathlib import Path

DOWNLOADS_DIR = Path(r"C:\Users\user\Downloads")

async def test_native_download():
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

        async def eval_js(js):
            res = await send('Runtime.evaluate', {
                'expression': js,
                'returnByValue': True,
                'awaitPromise': True
            })
            return res.get('result', {}).get('value')

        # Set download behavior to allow!
        print("Setting CDP download behavior to allow...")
        await send('Page.setDownloadBehavior', {
            'behavior': 'allow',
            'downloadPath': str(DOWNLOADS_DIR)
        })

        before_files = set(f.name for f in DOWNLOADS_DIR.glob("*"))

        # Find exact bounding rect of the download button
        rect = await eval_js("""
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const dl = btns.find(b => (b.innerText && b.innerText.includes('download')) || b.getAttribute('aria-label') === 'Download');
            if (!dl) return null;
            const r = dl.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
        })()
        """)
        print("Download button rect:", rect)
        if not rect:
            print("Download button not found!")
            return

        cx, cy = int(rect['x']), int(rect['y'])
        await send('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': cx, 'y': cy})
        await send('Input.dispatchMouseEvent', {'type': 'mousePressed', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
        await send('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
        await asyncio.sleep(1.5)

        # Find exact bounding rect of 720p option
        rect_720 = await eval_js("""
        (() => {
            const items = Array.from(document.querySelectorAll('button, [role="menuitem"], .mat-mdc-menu-item, span'));
            const opt720 = items.find(i => i.innerText && i.innerText.includes('720p'));
            if (!opt720) return null;
            const r = opt720.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2, text: opt720.innerText };
        })()
        """)
        print("720p option rect:", rect_720)
        if rect_720:
            cx2, cy2 = int(rect_720['x']), int(rect_720['y'])
            await send('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': cx2, 'y': cy2})
            await send('Input.dispatchMouseEvent', {'type': 'mousePressed', 'button': 'left', 'clickCount': 1, 'x': cx2, 'y': cy2})
            await send('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'button': 'left', 'clickCount': 1, 'x': cx2, 'y': cy2})

        print("Waiting for download to appear...")
        for sec in range(12):
            await asyncio.sleep(1)
            current_files = set(f.name for f in DOWNLOADS_DIR.glob("*"))
            diff = current_files - before_files
            if diff:
                print(f"NEW FILE DOWNLOADED: {diff}")
                break
        else:
            print("No new file detected in Downloads.")

if __name__ == '__main__':
    asyncio.run(test_native_download())
