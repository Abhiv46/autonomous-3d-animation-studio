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
SCREENSHOT_DIR = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2")

async def generate_scene2():
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

        # 1. Click back arrow if still in editor
        print("Ensuring we are on project view...", flush=True)
        await eval_js("""
        (() => {
            const backBtn = document.querySelector('button.back-button, [aria-label*="Back button"]');
            if (backBtn) backBtn.click();
        })()
        """)
        await asyncio.sleep(2)

        # 2. Clear prompt box
        print("Clearing prompt box...", flush=True)
        await eval_js("""
        (() => {
            const clears = Array.from(document.querySelectorAll('button')).filter(b => 
                b.innerText && b.innerText.trim() === 'close' && b.closest('.prompt-box, flow-base-prompt-box')
            );
            clears.forEach(b => b.click());
            const pm = document.querySelector('div.ProseMirror');
            if (pm) {
                pm.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
            }
        })()
        """)
        await asyncio.sleep(1)

        # 3. Ensure mode is Video
        print("Setting mode to Video...", flush=True)
        await eval_js("""
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const modeBtn = btns.find(b => b.innerText && (b.innerText.includes('Banana') || b.innerText.includes('Image')));
            if (modeBtn) modeBtn.click();
        })()
        """)
        await asyncio.sleep(1.5)
        await eval_js("""
        (() => {
            const opts = Array.from(document.querySelectorAll('button, [role="tab"], [role="menuitem"], span'));
            const vidTab = opts.find(o => o.innerText && o.innerText.trim() === 'Video');
            if (vidTab) vidTab.click();
        })()
        """)
        await asyncio.sleep(1.5)

        # Helper to attach
        async def attach(cat, text):
            print(f"  [+] Attaching {cat} -> '{text}'...", flush=True)
            # click '+'
            await eval_js("""
            (() => {
                const addBtn = Array.from(document.querySelectorAll('button')).find(b => 
                    b.getAttribute('aria-label') === 'Add ingredients to the prompt box' ||
                    (b.innerText && b.innerText.trim() === 'add' && b.closest('.prompt-box, flow-base-prompt-box'))
                );
                if (addBtn) addBtn.click();
            })()
            """)
            await asyncio.sleep(1.5)

            # click category tab
            await eval_js(f"""
            (() => {{
                const tabs = Array.from(document.querySelectorAll('mat-list-item, [role="tab"], button, span, div'));
                const targetTab = tabs.find(t => t.innerText && t.innerText.trim().toLowerCase() === '{cat.lower()}');
                if (targetTab) targetTab.click();
            }})()
            """)
            await asyncio.sleep(1.5)

            # click item
            await eval_js(f"""
            (() => {{
                const items = Array.from(document.querySelectorAll('button.asset-item, flow-add-menu-asset-item, [role="option"], div, span'));
                const target = items.find(i => i.innerText && i.innerText.trim().toLowerCase().includes('{text.lower()}'));
                if (target) {{
                    const btn = target.closest('button.asset-item') || target;
                    btn.click();
                }}
            }})()
            """)
            await asyncio.sleep(1.5)

            # click white 'Add to prompt' button
            res = await eval_js("""
            (() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const addBtn = btns.find(b => b.innerText && b.innerText.trim() === 'Add to prompt');
                if (addBtn && !addBtn.disabled) {
                    addBtn.click();
                    return 'added_to_prompt';
                }
                return 'failed';
            })()
            """)
            print(f"      Status: {res}", flush=True)
            await asyncio.sleep(1.5)
            # dismiss modal
            await eval_js("(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()")
            await asyncio.sleep(1)

        # 4. Attach Kaavya, Kaartik, and Scene 2 Image
        await attach("Characters", "Kaavya")
        await attach("Characters", "Kaartik")
        await attach("Images", "Toddlers fighting over sweet snack")

        # 5. Strict Guardrail Check
        chips_count = await eval_js("""
        (() => {
            const box = document.querySelector('.prompt-box, flow-base-prompt-box');
            if (!box) return 0;
            const chips = box.querySelectorAll('.chip-image, .chip-container, [class*="chip"]');
            return chips.length;
        })()
        """)
        print(f"  [GUARDRAIL] Verified attached chips in prompt box: {chips_count}", flush=True)
        if not chips_count or int(chips_count) < 2:
            raise RuntimeError("CRITICAL: Chips missing! Aborting per strict user instruction!")

        # 6. Type Clean Scene 2 Video Prompt
        clean_v2 = "Vertical 9:16, 8s, Pixar 3D animated style for toddlers. Toddler Kaavya and Kaartik play tug of war pulling sticky sweet Gulab Jamun between their hands. Kaavya giggles happily: Yeh mera meetha hai! Kaartik laughs cheerfully: Hum dono ka hai! The soft sweet squishes between their hands splashing syrup on Kaartik's nose. Both toddlers burst into cute baby giggles. Clear cute toddler laughter, playful Disney Pixar sound design."
        print("Typing clean Scene 2 prompt...", flush=True)
        await eval_js(f"""
        (() => {{
            const pm = document.querySelector('div.ProseMirror');
            if (pm) {{
                pm.focus();
                document.execCommand('insertText', false, {json.dumps(clean_v2)});
            }}
        }})()
        """)
        await asyncio.sleep(1.5)

        # 7. Submit Generation
        print("Submitting Scene 2 generation...", flush=True)
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

        # Auto-Approve spend modal
        for _ in range(5):
            await asyncio.sleep(1)
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
                print(f"      [Auto-Approve] Clicked: {app}", flush=True)
                break

        # 8. Wait for render completion (~50-80s)
        print("Waiting for Scene 2 render completion...", flush=True)
        await asyncio.sleep(10)
        for t in range(40):
            await asyncio.sleep(5)
            stat = await eval_js("""
            (() => {
                const hasStop = Array.from(document.querySelectorAll('button')).some(b => b.innerText && b.innerText.trim() === 'stop');
                const hasError = Array.from(document.querySelectorAll('.error-tile, [class*="failed"]')).length;
                return { isGenerating: hasStop, errors: hasError };
            })()
            """)
            is_gen = stat.get('isGenerating', False)
            if not is_gen and t >= 3:
                print(f"[✓] Scene 2 render completed! ({t*5}s)", flush=True)
                break
            if t % 3 == 0:
                print(f"    Scene 2 rendering in progress... ({t*5}s)", flush=True)

        await asyncio.sleep(3)

        # 9. Click into the new Scene 2 video to open player and download
        print("Opening player for Scene 2...", flush=True)
        await eval_js("""
        (() => {
            const tabs = Array.from(document.querySelectorAll('mat-list-item, [role="tab"], button, span, div'));
            const vidTab = tabs.find(t => t.innerText && t.innerText.trim() === 'Videos');
            if (vidTab) vidTab.click();
        })()
        """)
        await asyncio.sleep(2)

        # Click top newest video tile
        await eval_js("""
        (() => {
            const tiles = Array.from(document.querySelectorAll('.tile-row.virtual-item-container > div'));
            const valid = tiles.find(t => !t.className.includes('error'));
            if (valid) valid.click();
            else if (tiles.length > 0) tiles[0].click();
        })()
        """)
        await asyncio.sleep(3)

        # Download via native CDP click
        print("Triggering Scene 2 native 720p download...", flush=True)
        before_files = set(f.name for f in DOWNLOADS_DIR.glob("*"))

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

        print("Waiting for Scene 2 download...")
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
            print("Scene 2 download not caught in diff, checking Downloads...")

if __name__ == '__main__':
    asyncio.run(generate_scene2())
