import asyncio
import json
import urllib.request
import websockets

PROMPT = "Vertical 9:16 aspect ratio, Pixar 3D animated comedy. Pinki relaxes on sofa with brown chocolate face mask and cucumber slices on eyes, resting peacefully. Kaavya and Kaartik sneak in quietly. Kaavya whispers in cute toddler Hindi: 'Bhaiyya dekho, Mummy ke munh par chocolate cake laga hai!' Kaartik giggles: 'Chalo taste karte hain!' (All character voices strictly in cheerful cute HINDI dialogues). Ultra-vibrant colors, Pixar 3D animation."

async def run():
    req = urllib.request.urlopen('http://127.0.0.1:9222/json/list')
    tabs = json.loads(req.read().decode())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    print(f"[1] Connecting to Flow WS: {ws_url}", flush=True)
    
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

        # 1. Type prompt into ProseMirror
        print("[2] Typing Scene 1 Video Prompt...", flush=True)
        type_res = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const pm = document.querySelector('div.ProseMirror');
                if (!pm) return 'no_pm';
                pm.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, """ + json.dumps(PROMPT) + """);
                return 'typed';
            })()
            """,
            'returnByValue': True
        })
        print(f"    Type result: {type_res.get('result', {}).get('value')}", flush=True)
        await asyncio.sleep(1.5)

        # 2. Get coordinates of arrow_forward generate button
        print("[3] Locating Generate button...", flush=True)
        rect_res = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const btn = document.querySelector('button.generate-icon-button, [aria-label="Start generation"]');
                if (!btn) return null;
                const r = btn.getBoundingClientRect();
                return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
            })()
            """,
            'returnByValue': True
        })
        rect = rect_res.get('result', {}).get('value')
        print(f"    Button center: {rect}", flush=True)
        if not rect:
            print("[!] Could not find generate button!")
            return

        cx, cy = int(rect['x']), int(rect['y'])
        
        # 3. Real CDP Mouse Click
        print(f"[4] Clicking Generate button at ({cx}, {cy})...", flush=True)
        await call('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': cx, 'y': cy})
        await asyncio.sleep(0.1)
        await call('Input.dispatchMouseEvent', {'type': 'mousePressed', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
        await asyncio.sleep(0.1)
        await call('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
        await asyncio.sleep(2)

        # 4. Handle any auto-approval modal
        print("[5] Handling approvals if prompted...", flush=True)
        for _ in range(5):
            app = await call('Runtime.evaluate', {
                'expression': """
                (() => {
                    const btns = Array.from(document.querySelectorAll('button, span, div'));
                    const always = btns.find(b => b.innerText && b.innerText.includes('Always approve'));
                    if (always && always.offsetParent !== null) {
                        always.click();
                        return 'always_approved';
                    }
                    const approve = btns.find(b => b.innerText && b.innerText.trim() === 'Approve');
                    if (approve && approve.offsetParent !== null) {
                        approve.click();
                        return 'approved';
                    }
                    return 'none';
                })()
                """,
                'returnByValue': True
            })
            val = app.get('result', {}).get('value')
            if val in ['always_approved', 'approved']:
                print(f"    [+] Clicked approval: {val}", flush=True)
                break
            await asyncio.sleep(1)

        # 5. Check if generation started
        status = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const spinners = document.querySelectorAll('.loading-percentage, [class*="progress"]').length;
                const pm = document.querySelector('div.ProseMirror');
                return {
                    spinners: spinners,
                    pm_len: pm ? pm.innerText.trim().length : 0
                };
            })()
            """,
            'returnByValue': True
        })
        print(f"[✓] Scene 1 Video Generation State: {json.dumps(status.get('result', {}).get('value'))}", flush=True)

if __name__ == '__main__':
    asyncio.run(run())
