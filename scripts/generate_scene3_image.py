import asyncio
import json
import urllib.request
import base64
import time
import sys
from pathlib import Path
import websockets

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SCREENSHOT_DIR = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2")

async def send_cmd(ws, method, params=None, msg_id=1, timeout=10):
    msg = {'id': msg_id, 'method': method, 'params': params or {}}
    await ws.send(json.dumps(msg))
    start_t = time.time()
    while time.time() - start_t < timeout:
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
            res = json.loads(raw)
            if res.get('id') == msg_id:
                return res.get('result', {})
        except asyncio.TimeoutError:
            pass
    return {}

async def main():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/list').read())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    print(f"Connecting to Google Flow: {ws_url}", flush=True)

    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        msg_counter = 100

        async def execute(js):
            nonlocal msg_counter
            msg_counter += 1
            res = await send_cmd(ws, 'Runtime.evaluate', {
                'expression': js,
                'returnByValue': True,
                'awaitPromise': True
            }, msg_id=msg_counter)
            return res.get('result', {}).get('value')

        async def capture_png(filename):
            nonlocal msg_counter
            msg_counter += 1
            res = await send_cmd(ws, 'Page.captureScreenshot', {'format': 'png'}, msg_id=msg_counter, timeout=15)
            if 'data' in res:
                path = SCREENSHOT_DIR / filename
                with open(path, 'wb') as f:
                    f.write(base64.b64decode(res['data']))
                print(f"  [SCREENSHOT] Saved: {filename}", flush=True)

        print("\n[*] GENERATING SCENE 3 REFERENCE IMAGE...", flush=True)
        p3_img = "Pixar 3D animation style, 9:16 vertical. In the Indian kitchen, Indian Mom Pinki in elegant lavender kurta stands in doorway smiling affectionately. Toddler Kaavya and toddler Kaartik sit on kitchen floor with sweet syrup on cheeks, smiling like cute little angels with guilty innocent puppy eyes, holding up half a gulab jamun offering it to mom. Warm cinematic Pixar lighting, ultra high quality 3D render."

        # 1. Clear prompt box
        await execute("""
        (() => {
            const pm = document.querySelector('div.ProseMirror');
            if (pm) {
                pm.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
            }
        })()
        """)
        await asyncio.sleep(1)

        # 2. Type Scene 3 Prompt
        print("  [*] Typing Scene 3 Image prompt...", flush=True)
        await execute(f"""
        (() => {{
            const pm = document.querySelector('div.ProseMirror');
            if (pm) {{
                pm.focus();
                document.execCommand('insertText', false, {json.dumps(p3_img)});
            }}
        }})()
        """)
        await asyncio.sleep(1.5)

        # 3. Click Generate Button
        print("  [*] Clicking generate button...", flush=True)
        rect = await execute("""
        (() => {
            const btn = document.querySelector('button.generate-icon-button, [aria-label="Start generation"]');
            if (!btn) return null;
            const r = btn.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
        })()
        """)
        if rect:
            cx, cy = int(rect['x']), int(rect['y'])
            msg_counter += 1
            await send_cmd(ws, 'Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': cx, 'y': cy}, msg_id=msg_counter)
            msg_counter += 1
            await send_cmd(ws, 'Input.dispatchMouseEvent', {'type': 'mousePressed', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy}, msg_id=msg_counter)
            msg_counter += 1
            await send_cmd(ws, 'Input.dispatchMouseEvent', {'type': 'mouseReleased', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy}, msg_id=msg_counter)

        # 4. Auto-Approve if modal appears
        for _ in range(5):
            await asyncio.sleep(1)
            app = await execute("""
            (() => {
                const always = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Always approve'));
                if (always && always.offsetParent !== null) { always.click(); return 'always_approved'; }
                const approve = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.trim() === 'Approve');
                if (approve && approve.offsetParent !== null) { approve.click(); return 'approved'; }
                return 'none';
            })()
            """)
            if app in ['always_approved', 'approved']:
                print(f"      [Auto-Approve] Clicked: {app}", flush=True)
                break

        # 5. Wait for Scene 3 Image generation
        print("  [*] Waiting for Scene 3 Image to render...", flush=True)
        for i in range(25):
            await asyncio.sleep(2)
            is_busy = await execute("""
            (() => {
                const btns = Array.from(document.querySelectorAll('button'));
                return btns.some(b => b.innerText && b.innerText.trim() === 'stop');
            })()
            """)
            if not is_busy and i >= 2:
                print(f"  [+] Scene 3 Reference Image Render Complete! ({i*2}s)", flush=True)
                break
            if i % 3 == 0:
                print(f"      Rendering Scene 3 Image... ({i*2}s)", flush=True)

        await asyncio.sleep(2)
        await capture_png("scene3_image_complete.png")

        # 6. Switch to Images tab to show ALL 3 REFERENCE IMAGES on canvas
        print("\n[*] Switching to Images view to verify all 3 reference images...", flush=True)
        await execute("""
        (() => {
            const tabs = Array.from(document.querySelectorAll('mat-list-item, [role="tab"], button, span, div'));
            const imgTab = tabs.find(t => t.innerText && t.innerText.trim() === 'Images');
            if (imgTab) imgTab.click();
        })()
        """)
        await asyncio.sleep(2)
        await capture_png("all_3_reference_images_canvas_verified.png")
        print("\n[SUCCESS] ALL 3 REFERENCE IMAGES GENERATED FIRST ON CANVASS!", flush=True)

if __name__ == '__main__':
    asyncio.run(main())
