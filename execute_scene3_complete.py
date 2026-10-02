import asyncio
import json
import urllib.request
import os
import websockets

IMAGE_PROMPT = "Vertical 9:16 aspect ratio, ultra-detailed Pixar 3D animated comedy. Sunlit living room. Exactly ONE Kaavya (3.5, pink frock, twin buns) standing in front, looking directly into the camera with a big adorable toddler smile, holding both thumbs up. Beside her, Exactly ONE Kaartik (5, yellow polo) smiling cheerfully at the camera waving his hand. In background on sofa, Exactly ONE Pinki (25, clean fresh smiling face, powder-blue kurti) smiling warmly at her children. Warm cinematic lighting, Pixar 3D animated cartoon style, vibrant pastel colors."

VIDEO_PROMPT = "Vertical 9:16 aspect ratio, Pixar 3D animated comedy. Pinki cleans her face and laughs warmly at her naughty kids. Kaavya and Kaartik hug Mummy. Then Kaavya and Kaartik turn directly towards the camera, looking at viewers with the sweetest toddler smiles. Kaavya giggles in cute baby Hindi: 'Dosto, agar Mummy ka chocolate prank pasand aaya, toh jaldi se video ko LIKE karo aur channel ko SUBSCRIBE karo!' Kaartik waves cheerfully: 'Bhaago, Papa bhi aa gaye!' (All voices strictly in cheerful cute HINDI toddler dialogues). Ultra-vibrant Pixar 3D animation."

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
        print("[2] Switching to Image Mode (Nano Banana 2 9:16)...", flush=True)
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Video') || b.innerText.includes('Banana')));
                if (btn) btn.click();
            })()
            """
        })
        await asyncio.sleep(1.5)

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

        await call('Runtime.evaluate', {
            'expression': "(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()"
        })
        await asyncio.sleep(1)

        print("[3] Typing Scene 3 9:16 Image Prompt...", flush=True)
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

        print("[4] Generating Scene 3 Reference Image...", flush=True)
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

        print("[5] Waiting for Scene 3 Reference Image to render...", flush=True)
        for _ in range(30):
            await asyncio.sleep(2)
            spin_res = await call('Runtime.evaluate', {
                'expression': "document.querySelectorAll('.loading-percentage').length",
                'returnByValue': True
            })
            if spin_res.get('result', {}).get('value', 0) == 0:
                print("    Scene 3 Reference Image rendered on canvas!", flush=True)
                break

        # ----------------------------------------------------
        # STEP 2: Switch to Video Mode (720p 8s 9:16) & Submit Video Prompt
        # ----------------------------------------------------
        print("[6] Switching to Video Mode (720p 8s 9:16)...", flush=True)
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Banana') || b.innerText.includes('Image')));
                if (btn) btn.click();
            })()
            """
        })
        await asyncio.sleep(1.5)

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

        await call('Runtime.evaluate', {
            'expression': "(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()"
        })
        await asyncio.sleep(1)

        print("[7] Typing Scene 3 Video Prompt with cute toddler LIKE CTA...", flush=True)
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

        print("[8] Submitting Scene 3 Video Generation...", flush=True)
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

        print("[+] Scene 3 Video Generation successfully launched! Polling progress...", flush=True)

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
                print("[+] Scene 3 Video Render Completed!", flush=True)
                break

        await asyncio.sleep(3)
        # Click the download button on the card / player
        print("[9] Clicking Download button...", flush=True)
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const dlBtn = Array.from(document.querySelectorAll('button, a')).find(b => 
                    (b.innerText && b.innerText.includes('download')) || 
                    b.getAttribute('aria-label') === 'Download'
                );
                if (dlBtn) dlBtn.click();
            })()
            """
        })
        await asyncio.sleep(1.5)

        # Click 720p Original size
        print("[10] Selecting 720p Original size...", flush=True)
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const btns = Array.from(document.querySelectorAll('cdk-overlay-container button, [role="menuitem"]'));
                const btn720 = btns.find(b => b.innerText && b.innerText.includes('720p'));
                if (btn720) btn720.click();
            })()
            """
        })
        await asyncio.sleep(5)

        # Grab newest download
        downloads_dir = Path(r"C:\Users\user\Downloads")
        recent = sorted(downloads_dir.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True)
        out_file = os.path.join(RAW_CLIPS_DIR, "ep22_scene3.mp4")
        if recent and recent[0].stat().st_size > 1000000:
            import shutil
            shutil.copy2(recent[0], out_file)
            print(f"[SUCCESS] Scene 3 MP4 downloaded: {out_file} ({os.path.getsize(out_file)} bytes)", flush=True)
        else:
            print("[!] Download file not detected in Downloads folder!")

        await call('Runtime.evaluate', {
            'expression': "(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()"
        })

if __name__ == '__main__':
    from pathlib import Path
    asyncio.run(run())
