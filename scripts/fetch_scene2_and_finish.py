import asyncio
import json
import urllib.request
import websockets
import time
import shutil
import subprocess
from pathlib import Path
import imageio_ffmpeg

DOWNLOADS_DIR = Path(r"C:\Users\user\Downloads")
RAW_CLIPS_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips")
OUTPUT_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

async def download_scene2_and_stitch():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/list').read())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    print(f"Connecting to Flow: {ws_url}", flush=True)

    async with websockets.connect(ws_url, max_size=50*1024*1024, open_timeout=6) as ws:
        msg_id = 0
        async def send(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cur_id = msg_id
            await ws.send(json.dumps({'id': cur_id, 'method': method, 'params': params or {}}))
            while True:
                res = json.loads(await asyncio.wait_for(ws.recv(), timeout=8.0))
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
        print("Ensuring Videos tab is active...", flush=True)
        await eval_js("""
        (() => {
            const tabs = Array.from(document.querySelectorAll('mat-list-item, [role="tab"], button, span, div'));
            const vidTab = tabs.find(t => t.innerText && t.innerText.trim() === 'Videos');
            if (vidTab) vidTab.click();
        })()
        """)
        await asyncio.sleep(2)

        # Click top-left video tile (Scene 2)
        print("Clicking top-left video tile...", flush=True)
        await eval_js("""
        (() => {
            const tiles = Array.from(document.querySelectorAll('.tile-row.virtual-item-container > div'));
            const valid = tiles.filter(t => !t.className.includes('error'));
            if (valid.length > 0) valid[0].click();
        })()
        """)
        await asyncio.sleep(3)

        before_files = set(f.name for f in DOWNLOADS_DIR.glob("*"))

        # Click Download button
        print("Clicking Download button...", flush=True)
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

    # -------------------------------------------------------------
    # STITCH ALL 3 SCENES PRESERVING 100% ORIGINAL FLOW AUDIO
    # -------------------------------------------------------------
    c1 = RAW_CLIPS_DIR / "ep22_scene1_real.mp4"
    c2 = RAW_CLIPS_DIR / "ep22_scene2_real.mp4"
    c3 = RAW_CLIPS_DIR / "ep22_scene3_real.mp4"

    print("\n=======================================================", flush=True)
    print("[*] STITCHING 3 SCENES PRESERVING 100% ORIGINAL FLOW AUDIO...", flush=True)
    print(f"    Scene 1: {c1} ({c1.stat().st_size if c1.exists() else 'missing'} bytes)", flush=True)
    print(f"    Scene 2: {c2} ({c2.stat().st_size if c2.exists() else 'missing'} bytes)", flush=True)
    print(f"    Scene 3: {c3} ({c3.stat().st_size if c3.exists() else 'missing'} bytes)", flush=True)
    print("=======================================================\n", flush=True)

    master_out = OUTPUT_DIR / "TheNaughtyDuo_EP22_OriginalAudio_Master.mp4"
    concat_list = RAW_CLIPS_DIR / "ep22_concat.txt"

    with open(concat_list, "w", encoding="utf-8") as f:
        f.write(f"file '{c1.resolve()}'\n")
        f.write(f"file '{c2.resolve()}'\n")
        f.write(f"file '{c3.resolve()}'\n")

    cmd = [
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(master_out)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[🎉 MASTERPIECE READY] {master_out} ({master_out.stat().st_size} bytes / {master_out.stat().st_size/(1024*1024):.2f} MB)")
    else:
        print("Re-encoding with concat filter to preserve 100% original audio...", flush=True)
        cmd_filter = [
            FFMPEG, "-y",
            "-i", str(c1),
            "-i", str(c2),
            "-i", str(c3),
            "-filter_complex", "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[outv][outa]",
            "-map", "[outv]",
            "-map", "[outa]",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-pix_fmt", "yuv420p",
            str(master_out)
        ]
        res2 = subprocess.run(cmd_filter, capture_output=True, text=True)
        if res2.returncode == 0:
            print(f"[🎉 MASTERPIECE READY] {master_out} ({master_out.stat().st_size} bytes / {master_out.stat().st_size/(1024*1024):.2f} MB)")
        else:
            print(f"Stitch error: {res2.stderr}")

if __name__ == '__main__':
    asyncio.run(download_scene2_and_stitch())
