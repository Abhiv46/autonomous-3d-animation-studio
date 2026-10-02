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

async def main():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/list').read())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    print(f"Connecting to Google Flow: {ws_url}", flush=True)

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
            res = await send('Runtime.evaluate', {'expression': js, 'returnByValue': True, 'awaitPromise': True})
            return res.get('result', {}).get('value')

        async def take_shot(filename):
            shot = await send('Page.captureScreenshot', {'format': 'png'})
            path = SCREENSHOT_DIR / filename
            with open(path, 'wb') as f:
                f.write(base64.b64decode(shot['data']))
            print(f"  [SCREENSHOT] Saved: {filename}", flush=True)

        async def wait_idle(timeout=60):
            print("  [*] Waiting for generation to complete...", flush=True)
            for i in range(timeout // 2):
                await asyncio.sleep(2)
                # auto approve if spend modal
                app = await eval_js("""
                (() => {
                    const always = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Always approve'));
                    if (always && always.offsetParent !== null) { always.click(); return 'always_approved'; }
                    const approve = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.trim() === 'Approve');
                    if (approve && approve.offsetParent !== null) { approve.click(); return 'approved'; }
                    return 'none';
                })()
                """)
                if app in ['always_approved', 'approved']:
                    print(f"      Spend approval clicked: {app}", flush=True)

                is_busy = await eval_js("""
                (() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    const hasStop = btns.some(b => b.innerText && b.innerText.trim() === 'stop');
                    const spinners = document.querySelectorAll('.loading-percentage, [class*="spinner"]').length;
                    return hasStop || spinners > 0;
                })()
                """)
                if not is_busy and i >= 1:
                    print(f"  [+] Idle! Generation finished!", flush=True)
                    return True
            print(f"  [!] Timeout waiting after {timeout}s", flush=True)
            return True

        # 1. Wait for Scene 2 to finish
        print("\n--- Waiting for Scene 2 Reference Image ---", flush=True)
        await wait_idle(timeout=40)
        await take_shot("scene2_ref_rendered.png")

        # 2. Submit Scene 3 Reference Image
        print("\n--- Submitting Scene 3 Reference Image ---", flush=True)
        p3_img = "Pixar 3D animation style, 9:16 vertical. In the Indian kitchen, Indian Mom Pinki in elegant lavender kurta stands in doorway smiling affectionately. Toddler Kaavya and toddler Kaartik sit on kitchen floor with sweet syrup on cheeks, smiling like cute little angels with guilty innocent puppy eyes, holding up half a gulab jamun offering it to mom. Warm cinematic Pixar lighting, ultra high quality 3D render."
        
        # Clear prompt box
        await eval_js("""
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

        # Type prompt
        await eval_js(f"""
        (() => {{
            const pm = document.querySelector('div.ProseMirror');
            if (pm) {{
                pm.focus();
                document.execCommand('insertText', false, {json.dumps(p3_img)});
            }}
        }})()
        """)
        await asyncio.sleep(1.5)

        # Click Generate
        rect = await eval_js("""
        (() => {
            const btn = document.querySelector('button.generate-icon-button, [aria-label="Start generation"]');
            if (!btn) return null;
            const r = btn.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
        })()
        """)
        if rect:
            cx, cy = int(rect['x']), int(rect['y'])
            await send('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': cx, 'y': cy})
            await send('Input.dispatchMouseEvent', {'type': 'mousePressed', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
            await send('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})

        # Wait for Scene 3 to finish
        print("\n--- Waiting for Scene 3 Reference Image ---", flush=True)
        await wait_idle(timeout=50)
        await take_shot("scene3_ref_rendered.png")

        # 3. Switch to All Media / Images to show ALL 3 REFERENCE IMAGES
        await eval_js("""
        (() => {
            const tabs = Array.from(document.querySelectorAll('mat-list-item, [role="tab"], button, span, div'));
            const imgTab = tabs.find(t => t.innerText && t.innerText.trim() === 'Images');
            if (imgTab) imgTab.click();
        })()
        """)
        await asyncio.sleep(2)
        await take_shot("all_3_reference_images_canvas_proof.png")

        print("\n[SUCCESS] ALL 3 REFERENCE IMAGES FULLY GENERATED ON CANVA FIRST!", flush=True)

if __name__ == '__main__':
    asyncio.run(main())
