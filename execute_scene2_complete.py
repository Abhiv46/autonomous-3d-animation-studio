import asyncio
import json
import urllib.request
import os
import websockets

IMAGE_PROMPT = "Vertical 9:16 aspect ratio, ultra-detailed Pixar 3D animated comedy. Sunlit living room. Exactly ONE Kaavya (3.5, pink frock, twin buns) with a shocked funny face, tongue sticking out, looking at her muddy finger in disgust. Beside her, Exactly ONE Kaartik (5, yellow polo) pointing his finger at Kaavya and laughing hysterically with tears in his eyes. On sofa, Exactly ONE Pinki (25, mother, powder-blue kurti, brown clay face mask) lifting one cucumber slice off her eye in surprised shock. Cinematic Pixar 3D lighting, vibrant saturated colors, expressive cartoon faces."

VIDEO_PROMPT = "Vertical 9:16 aspect ratio, Pixar 3D animated comedy. Kaavya tastes the chocolate clay from her finger, her eyes go wide with hilarious toddler shock! Kaavya cries out in cute toddler Hindi: 'Chi chi! Ye chocolate nahi hai, ye toh mitti hai!' Kaartik rolls on the sofa laughing: 'Hahaha! Mummy ne chocolate nahi, mitti lagayi hai!' Pinki lifts cucumber slice off her eye in shock: 'Kaavya! Tumne mera mask chaat liya?!' (All character voices strictly in cheerful cute HINDI dialogues). Ultra-vibrant Pixar 3D animation."

RAW_CLIPS_DIR = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips"

async def run():
    req = urllib.request.urlopen('http://127.0.0.1:9222/json/list')
    tabs = json.loads(req.read().decode())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    print(f"[1] Connected to Flow Tab: {ws_url}", flush=True)
    
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

        # Dismiss any open dialogs/popovers
        await call('Runtime.evaluate', {
            'expression': "(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()"
        })
        await asyncio.sleep(1)

        # ----------------------------------------------------
        # STEP 1: Switch to Image Mode & Generate Reference 3D Image
        # ----------------------------------------------------
        print("[2] Switching to Image Mode (Nano Banana 2 · 9:16)...", flush=True)
        # Click mode trigger
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Video') || b.innerText.includes('Banana')));
                if (btn) btn.click();
            })()
            """
        })
        await asyncio.sleep(1.5)

        # Click Image tab
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const candidates = Array.from(document.querySelectorAll("button, [role='tab'], span"));
                const imgTab = candidates.find(c => c.innerText && c.innerText.trim() === 'Image');
                if (imgTab) imgTab.click();
            })()
            """
        })
        await asyncio.sleep(1)

        # Dismiss popover
        await call('Runtime.evaluate', {
            'expression': "(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()"
        })
        await asyncio.sleep(1)

        # Type Scene 2 Image Prompt into ProseMirror
        print("[3] Typing Scene 2 9:16 Image Prompt...", flush=True)
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const pm = document.querySelector('div.ProseMirror');
                if (!pm) return 'no_pm';
                pm.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, """ + json.dumps(IMAGE_PROMPT) + """);
                return 'typed';
            })()
            """
        })
        await asyncio.sleep(1.5)

        # Click Generate button via CDP native mouse click
        print("[4] Generating Scene 2 Reference Image...", flush=True)
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
        if rect:
            cx, cy = int(rect['x']), int(rect['y'])
            await call('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': cx, 'y': cy})
            await asyncio.sleep(0.1)
            await call('Input.dispatchMouseEvent', {'type': 'mousePressed', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
            await asyncio.sleep(0.1)
            await call('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})

        # Wait for image generation (~15s)
        print("[5] Waiting for Scene 2 Reference Image to render...", flush=True)
        for _ in range(30):
            await asyncio.sleep(2)
            spin_res = await call('Runtime.evaluate', {
                'expression': "document.querySelectorAll('.loading-percentage').length",
                'returnByValue': True
            })
            if spin_res.get('result', {}).get('value', 0) == 0:
                print("    Scene 2 Reference Image rendered on canvas!", flush=True)
                break

        # ----------------------------------------------------
        # STEP 2: Switch to Video Mode (720p 8s 9:16) & Submit Video Prompt
        # ----------------------------------------------------
        print("[6] Switching to Video Mode (720p 8s 9:16)...", flush=True)
        # Click mode trigger
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Banana') || b.innerText.includes('Image')));
                if (btn) btn.click();
            })()
            """
        })
        await asyncio.sleep(1.5)

        # Click Video tab
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const candidates = Array.from(document.querySelectorAll("button, [role='tab'], span"));
                const vidTab = candidates.find(c => c.innerText && c.innerText.trim() === 'Video');
                if (vidTab) vidTab.click();
            })()
            """
        })
        await asyncio.sleep(1)

        # Dismiss popover
        await call('Runtime.evaluate', {
            'expression': "(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()"
        })
        await asyncio.sleep(1)

        # Type Scene 2 Video Prompt
        print("[7] Typing Scene 2 Video Prompt with cute toddler Hindi dialogues...", flush=True)
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const pm = document.querySelector('div.ProseMirror');
                if (!pm) return 'no_pm';
                pm.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, """ + json.dumps(VIDEO_PROMPT) + """);
                return 'typed';
            })()
            """
        })
        await asyncio.sleep(1.5)

        # Click Generate button
        print("[8] Submitting Scene 2 Video Generation...", flush=True)
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
        if rect:
            cx, cy = int(rect['x']), int(rect['y'])
            await call('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': cx, 'y': cy})
            await asyncio.sleep(0.1)
            await call('Input.dispatchMouseEvent', {'type': 'mousePressed', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
            await asyncio.sleep(0.1)
            await call('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
        await asyncio.sleep(2)

        # Auto-approvals check
        for _ in range(5):
            app = await call('Runtime.evaluate', {
                'expression': """
                (() => {
                    const always = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Always approve'));
                    if (always && always.offsetParent !== null) { always.click(); return 'always_approved'; }
                    const approve = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.trim() === 'Approve');
                    if (approve && approve.offsetParent !== null) { approve.click(); return 'approved'; }
                    return 'none';
                })()
                """,
                'returnByValue': True
            })
            if app.get('result', {}).get('value') in ['always_approved', 'approved']:
                print(f"    Auto-approval confirmed: {app.get('result', {}).get('value')}", flush=True)
                break
            await asyncio.sleep(1)

        print("[✓] Scene 2 Video Generation successfully launched! Polling progress...", flush=True)

        # Wait for video generation to complete
        for minute in range(35):
            await asyncio.sleep(6)
            stat = await call('Runtime.evaluate', {
                'expression': """
                (() => {
                    const p = Array.from(document.querySelectorAll('.loading-percentage, [class*="progress"], [class*="percent"]')).map(e => e.innerText ? e.innerText.trim() : '');
                    const spinners = document.querySelectorAll('.loading-percentage').length;
                    return { p, spinners };
                })()
                """,
                'returnByValue': True
            })
            data = stat.get('result', {}).get('value', {})
            p_text = data.get('p', [])
            spin = data.get('spinners', 0)
            if p_text:
                print(f"    Progress: {p_text[0]}", flush=True)
            if spin == 0 and minute > 2:
                print("[+] Scene 2 Video Render Completed!", flush=True)
                break

        # Harvest Scene 2 video URL
        await asyncio.sleep(3)
        vid_info = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const imgs = Array.from(document.querySelectorAll('img')).filter(i => i.src && i.src.includes('flow-content.google/image'));
                // Click top newest video card
                if (imgs.length > 0) {
                    const card = imgs[0].closest('[class*="card"], [class*="item"], div:has(> img)');
                    if (card) card.click();
                }
            })()
            """
        })
        await asyncio.sleep(2)

        media = await call('Runtime.evaluate', {
            'expression': "document.querySelector('video') ? document.querySelector('video').src : null",
            'returnByValue': True
        })
        vid_url = media.get('result', {}).get('value')
        print(f"Scene 2 Video URL: {vid_url}", flush=True)

        if vid_url:
            out_file = os.path.join(RAW_CLIPS_DIR, "ep22_scene2.mp4")
            urllib.request.urlretrieve(vid_url, out_file)
            print(f"[SUCCESS] Scene 2 MP4 downloaded: {out_file} ({os.path.getsize(out_file)} bytes)", flush=True)

        # Dismiss modal
        await call('Runtime.evaluate', {
            'expression': "(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()"
        })

if __name__ == '__main__':
    asyncio.run(run())
