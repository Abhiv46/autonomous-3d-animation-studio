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

async def download_scene2():
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

        # Switch to Videos tab
        print("Clicking Videos tab...", flush=True)
        await eval_js("""
        (() => {
            const tabs = Array.from(document.querySelectorAll('mat-list-item, [role="tab"], button, span, div'));
            const vidTab = tabs.find(t => t.innerText && t.innerText.trim() === 'Videos');
            if (vidTab) vidTab.click();
        })()
        """)
        await asyncio.sleep(2)

        # Click top newest video card (which is Scene 2)
        print("Clicking top newest video tile...", flush=True)
        await eval_js("""
        (() => {
            const tiles = Array.from(document.querySelectorAll('.tile-row.virtual-item-container > div'));
            // find newest non-error tile
            const valid = tiles.filter(t => !t.className.includes('error'));
            if (valid.length > 0) valid[0].click();
            else if (tiles.length > 0) tiles[0].click();
        })()
        """)
        await asyncio.sleep(3)

        before_files = set(f.name for f in DOWNLOADS_DIR.glob("*"))

        # Click Download button
        print("Clicking download button...", flush=True)
        rect_dl = await eval_js("""
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const dl = btns.find(b => (b.innerText && b.innerText.includes('download')) || b.getAttribute('aria-label') === 'Download');
            if (!dl) return null;
            const r = dl.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
        })()
        """)
        if rect_dl:
            cx, cy = int(rect_dl['x']), int(rect_dl['y'])
            await send('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': cx, 'y': cy})
            await send('Input.dispatchMouseEvent', {'type': 'mousePressed', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
            await send('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
        await asyncio.sleep(1.5)

        # Click 720p option
        print("Clicking 720p option...", flush=True)
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

        print("Waiting for Scene 2 download to finish...", flush=True)
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
            print(f"[SUCCESS] Scene 2 downloaded: {target} ({target.stat().st_size} bytes)")
        else:
            print("[FAIL] Scene 2 not downloaded!")

if __name__ == '__main__':
    asyncio.run(download_scene2())
