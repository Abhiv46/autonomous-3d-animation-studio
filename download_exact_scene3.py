import asyncio
import json
import urllib.request
import os
import shutil
from pathlib import Path
import websockets

RAW_CLIPS_DIR = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips"

async def run():
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

        # Dismiss any open modal
        await call('Runtime.evaluate', {
            'expression': "(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()"
        })
        await asyncio.sleep(1)

        # Record files in Downloads before clicking
        downloads_dir = Path(r"C:\Users\user\Downloads")
        before_files = set(f.name for f in downloads_dir.glob("*"))

        # Click the Scene 3 card
        print("[1] Clicking Scene 3 video card...", flush=True)
        click_res = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const img = Array.from(document.querySelectorAll('img')).find(i => i.src && i.src.includes('bcd9a3ec'));
                if (!img) return 'not found';
                const card = img.closest('[class*="card"], [class*="item"], div');
                const playBtn = card ? card.querySelector('button, [aria-label*="play" i], mat-icon') : null;
                if (playBtn) { playBtn.click(); return 'clicked_play'; }
                if (card) { card.click(); return 'clicked_card'; }
                img.click();
                return 'clicked_img';
            })()
            """,
            'returnByValue': True
        })
        print(f"    Click result: {click_res.get('result', {}).get('value')}", flush=True)
        await asyncio.sleep(2)

        # Click Download button
        print("[2] Clicking Download button...", flush=True)
        dl_res = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const dlBtn = Array.from(document.querySelectorAll('button, a')).find(b => 
                    (b.innerText && b.innerText.includes('download')) || 
                    b.getAttribute('aria-label') === 'Download'
                );
                if (dlBtn) { dlBtn.click(); return 'clicked_dl'; }
                return 'not_found';
            })()
            """,
            'returnByValue': True
        })
        print(f"    Download btn: {dl_res.get('result', {}).get('value')}", flush=True)
        await asyncio.sleep(1.5)

        # Click 720p Original size
        print("[3] Clicking 720p Original size...", flush=True)
        opt_res = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const btns = Array.from(document.querySelectorAll('cdk-overlay-container button, [role="menuitem"]'));
                const btn720 = btns.find(b => b.innerText && b.innerText.includes('720p'));
                if (btn720) { btn720.click(); return 'clicked_720'; }
                return 'not_found';
            })()
            """,
            'returnByValue': True
        })
        print(f"    720p click: {opt_res.get('result', {}).get('value')}", flush=True)
        
        # Wait up to 15s for the new download to appear
        print("[4] Waiting for download to finish...", flush=True)
        downloaded_file = None
        for _ in range(15):
            await asyncio.sleep(1)
            current_files = set(f.name for f in downloads_dir.glob("*"))
            new_files = current_files - before_files
            for nf in new_files:
                p = downloads_dir / nf
                if p.is_file() and p.stat().st_size > 1000000:
                    downloaded_file = p
                    break
            if downloaded_file:
                break

        if downloaded_file:
            target_path = os.path.join(RAW_CLIPS_DIR, "ep22_scene3.mp4")
            shutil.copy2(downloaded_file, target_path)
            print(f"[SUCCESS] Scene 3 MP4 downloaded: {target_path} ({os.path.getsize(target_path)} bytes)", flush=True)
        else:
            # Fallback: check most recently modified file in downloads
            recent = sorted(downloads_dir.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True)
            if recent and recent[0].stat().st_size > 1000000:
                target_path = os.path.join(RAW_CLIPS_DIR, "ep22_scene3.mp4")
                shutil.copy2(recent[0], target_path)
                print(f"[SUCCESS via Fallback] Scene 3 MP4: {target_path} ({os.path.getsize(target_path)} bytes)", flush=True)

        # Close preview modal
        await call('Runtime.evaluate', {
            'expression': "(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()"
        })

if __name__ == '__main__':
    asyncio.run(run())
