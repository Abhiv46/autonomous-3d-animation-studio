import asyncio
import json
import urllib.request
import websockets
import time
import shutil
from pathlib import Path

DOWNLOADS_DIR = Path(r"C:\Users\user\Downloads")
RAW_CLIPS_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips")

async def download_scene1():
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

        await send('Page.setDownloadBehavior', {
            'behavior': 'allow',
            'downloadPath': str(DOWNLOADS_DIR)
        })

        # Click thumbnail for Scene 1 (Toddler reaching for gulab jamun)
        print("Clicking thumbnail for Scene 1...")
        await eval_js("""
        (() => {
            const btns = Array.from(document.querySelectorAll('button.thumbnail-button'));
            const target = btns.find(b => b.getAttribute('aria-label') && b.getAttribute('aria-label').includes('Toddler reaching for gulab jamun'));
            if (target) target.click();
        })()
        """)
        await asyncio.sleep(2)

        before_files = set(f.name for f in DOWNLOADS_DIR.glob("*"))

        # Click Download button
        rect = await eval_js("""
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const dl = btns.find(b => (b.innerText && b.innerText.includes('download')) || b.getAttribute('aria-label') === 'Download');
            if (!dl) return null;
            const r = dl.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
        })()
        """)
        if rect:
            cx, cy = int(rect['x']), int(rect['y'])
            await send('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': cx, 'y': cy})
            await send('Input.dispatchMouseEvent', {'type': 'mousePressed', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
            await send('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
        await asyncio.sleep(1.5)

        # Click 720p option
        rect_720 = await eval_js("""
        (() => {
            const items = Array.from(document.querySelectorAll('button, [role="menuitem"], .mat-mdc-menu-item, span'));
            const opt720 = items.find(i => i.innerText && i.innerText.includes('720p'));
            if (!opt720) return null;
            const r = opt720.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
        })()
        """)
        if rect_720:
            cx2, cy2 = int(rect_720['x']), int(rect_720['y'])
            await send('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': cx2, 'y': cy2})
            await send('Input.dispatchMouseEvent', {'type': 'mousePressed', 'button': 'left', 'clickCount': 1, 'x': cx2, 'y': cy2})
            await send('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'button': 'left', 'clickCount': 1, 'x': cx2, 'y': cy2})

        print("Waiting for Scene 1 download...")
        downloaded = None
        for _ in range(12):
            await asyncio.sleep(1)
            diff = set(f.name for f in DOWNLOADS_DIR.glob("*")) - before_files
            for fn in diff:
                p = DOWNLOADS_DIR / fn
                if p.is_file() and p.suffix.lower() == '.mp4' and p.stat().st_size > 500000:
                    downloaded = p
                    break
            if downloaded:
                break

        if downloaded:
            target = RAW_CLIPS_DIR / "ep22_scene1_real.mp4"
            shutil.copy2(downloaded, target)
            print(f"[SUCCESS] Scene 1 downloaded: {target} ({target.stat().st_size} bytes)")
        else:
            print("Download not found!")

if __name__ == '__main__':
    asyncio.run(download_scene1())
