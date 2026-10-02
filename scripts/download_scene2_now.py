import asyncio
import json
import urllib.request
import websockets
import time
import shutil
import sys
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DOWNLOADS_DIR = Path(r"C:\Users\user\Downloads")
RAW_CLIPS_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips")
SCREENSHOT_DIR = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2")

async def main():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/list').read())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    print(f"Connecting to Flow: {ws_url}", flush=True)

    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        msg_id = 0
        async def send(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cur_id = msg_id
            await ws.send(json.dumps({'id': cur_id, 'method': method, 'params': params or {}}))
            while True:
                res = json.loads(await asyncio.wait_for(ws.recv(), timeout=10.0))
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

        # Find center of the first card (Scene 2)
        rect = await eval_js("""
        (() => {
            const row = document.querySelector('.tile-row.virtual-item-container');
            if (!row) return null;
            const firstTile = row.children[0];
            if (!firstTile) return null;
            const r = firstTile.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2, w: r.width, h: r.height };
        })()
        """)
        print("First tile rect:", rect, flush=True)
        if not rect:
            print("First tile not found!", flush=True)
            return

        cx, cy = int(rect['x']), int(rect['y'])
        print(f"Clicking Scene 2 card at ({cx}, {cy})...", flush=True)
        await send('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': cx, 'y': cy})
        await send('Input.dispatchMouseEvent', {'type': 'mousePressed', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
        await send('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
        await asyncio.sleep(3)

        before_files = set(f.name for f in DOWNLOADS_DIR.glob("*"))

        # Find Download button
        rect_dl = await eval_js("""
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const dl = btns.find(b => (b.innerText && b.innerText.includes('download')) || b.getAttribute('aria-label') === 'Download');
            if (!dl) return null;
            const r = dl.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
        })()
        """)
        print("Download button rect:", rect_dl, flush=True)
        if rect_dl:
            cx_dl, cy_dl = int(rect_dl['x']), int(rect_dl['y'])
            await send('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': cx_dl, 'y': cy_dl})
            await send('Input.dispatchMouseEvent', {'type': 'mousePressed', 'button': 'left', 'clickCount': 1, 'x': cx_dl, 'y': cy_dl})
            await send('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'button': 'left', 'clickCount': 1, 'x': cx_dl, 'y': cy_dl})
            await asyncio.sleep(1.5)

            # Find 720p option
            rect_720 = await eval_js("""
            (() => {
                const items = Array.from(document.querySelectorAll('button, [role="menuitem"], .mat-mdc-menu-item, span'));
                const opt720 = items.find(i => i.innerText && i.innerText.includes('720p'));
                if (!opt720) return null;
                const r = opt720.getBoundingClientRect();
                return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
            })()
            """)
            print("720p option rect:", rect_720, flush=True)
            if rect_720:
                cx_720, cy_720 = int(rect_720['x']), int(rect_720['y'])
                await send('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': cx_720, 'y': cy_720})
                await send('Input.dispatchMouseEvent', {'type': 'mousePressed', 'button': 'left', 'clickCount': 1, 'x': cx_720, 'y': cy_720})
                await send('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'button': 'left', 'clickCount': 1, 'x': cx_720, 'y': cy_720})

        print("Waiting for Scene 2 download to appear...", flush=True)
        downloaded = None
        for _ in range(15):
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
            target = RAW_CLIPS_DIR / "ep22_scene2_real.mp4"
            shutil.copy2(downloaded, target)
            print(f"[SUCCESS] Scene 2 saved: {target} ({target.stat().st_size} bytes)", flush=True)
        else:
            print("Download not found!", flush=True)

if __name__ == '__main__':
    asyncio.run(main())
