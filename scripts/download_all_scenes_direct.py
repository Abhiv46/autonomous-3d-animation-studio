import asyncio
import json
import urllib.request
import base64
import time
import shutil
from pathlib import Path
import websockets

DOWNLOADS_DIR = Path(r"C:\Users\user\Downloads")
RAW_CLIPS_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips")
RAW_CLIPS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOT_DIR = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2")

SCENES = [
    {
        "num": 1,
        "aria": "Toddler reaching for gulab jamun",
        "out": "ep22_scene1.mp4"
    },
    {
        "num": 2,
        "aria": "Toddlers play tug of war",
        "out": "ep22_scene2.mp4"
    },
    {
        "num": 3,
        "aria": "Toddlers offering sweet to mom",
        "out": "ep22_scene3.mp4"
    }
]

async def download_scenes():
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

        for sc in SCENES:
            s_num = sc['num']
            aria_txt = sc['aria']
            out_file = sc['out']
            print(f"\n[*] Downloading Scene {s_num}: '{aria_txt}' -> {out_file}...", flush=True)

            # 1. Click thumbnail button in carousel
            clicked = await eval_js(f"""
            (() => {{
                const btns = Array.from(document.querySelectorAll('button.thumbnail-button'));
                const target = btns.find(b => b.getAttribute('aria-label') && b.getAttribute('aria-label').includes('{aria_txt}'));
                if (target) {{
                    target.click();
                    return 'clicked thumbnail: ' + target.getAttribute('aria-label');
                }}
                return 'not found';
            }})()
            """)
            print(f"    Carousel click: {clicked}", flush=True)
            await asyncio.sleep(2)

            before_files = set(f.name for f in DOWNLOADS_DIR.glob("*"))

            # 2. Click Download button at top right
            dl_res = await eval_js("""
            (() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const dl = btns.find(b => (b.innerText && b.innerText.includes('download')) || b.getAttribute('aria-label') === 'Download');
                if (dl) {
                    dl.click();
                    return 'clicked download button';
                }
                return 'dl button not found';
            })()
            """)
            print(f"    Download menu trigger: {dl_res}", flush=True)
            await asyncio.sleep(1.5)

            # 3. Click 720p option in menu
            opt_res = await eval_js("""
            (() => {
                const items = Array.from(document.querySelectorAll('button, [role="menuitem"], .mat-mdc-menu-item, span'));
                const opt720 = items.find(i => i.innerText && i.innerText.includes('720p'));
                if (opt720) {
                    opt720.click();
                    return 'clicked 720p';
                }
                return '720p not found';
            })()
            """)
            print(f"    Quality click: {opt_res}", flush=True)

            # 4. Wait for download
            target_path = RAW_CLIPS_DIR / out_file
            downloaded = None
            for _ in range(15):
                await asyncio.sleep(1)
                current_files = set(f.name for f in DOWNLOADS_DIR.glob("*"))
                diff = current_files - before_files
                for fn in diff:
                    p = DOWNLOADS_DIR / fn
                    if p.is_file() and p.suffix.lower() == '.mp4' and p.stat().st_size > 500000:
                        downloaded = p
                        break
                if downloaded:
                    break

            if downloaded:
                shutil.copy2(downloaded, target_path)
                print(f"    [SUCCESS] Scene {s_num} saved: {target_path} ({target_path.stat().st_size} bytes)", flush=True)
            else:
                print(f"    [WARNING] Scene {s_num} did not download new file, checking most recent...", flush=True)

            await asyncio.sleep(1.5)

if __name__ == '__main__':
    asyncio.run(download_scenes())
