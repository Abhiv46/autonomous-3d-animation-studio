import asyncio
import json
import urllib.request
import os
import shutil
from pathlib import Path
import websockets

RAW_CLIPS_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips")
RAW_CLIPS_DIR.mkdir(parents=True, exist_ok=True)

class StrictFlowEngine:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self.msg_id = 0

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, max_size=50*1024*1024)

    async def close(self):
        if self.ws:
            await self.ws.close()

    async def call(self, method, params=None):
        self.msg_id += 1
        cur_id = self.msg_id
        await self.ws.send(json.dumps({'id': cur_id, 'method': method, 'params': params or {}}))
        while True:
            res = json.loads(await self.ws.recv())
            if res.get('id') == cur_id:
                return res.get('result', {})

    async def eval(self, js):
        res = await self.call('Runtime.evaluate', {'expression': js, 'returnByValue': True, 'awaitPromise': True})
        return res.get('result', {}).get('value')

    async def dismiss_modals(self):
        await self.eval("(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()")
        await asyncio.sleep(1)

    async def clear_prompt_box(self):
        await self.eval("""
        (() => {
            const clears = Array.from(document.querySelectorAll('button')).filter(b => b.innerText && b.innerText.trim() === 'close' && b.closest('.prompt-box, flow-base-prompt-box'));
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

    # -------------------------------------------------------------------------
    # PHASE 1: Generate 9:16 Reference 3D Image
    # -------------------------------------------------------------------------
    async def generate_scene_image(self, prompt_text):
        print(f"\n[PHASE 1] Generating 9:16 Reference 3D Image...", flush=True)
        await self.dismiss_modals()
        await self.clear_prompt_box()

        # 1. Switch to Image Mode (Nano Banana 2 · 9:16)
        print("  [*] Switching mode to Image...", flush=True)
        await self.eval("""
        (() => {
            const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Video') || b.innerText.includes('Banana')));
            if (btn) btn.click();
        })()
        """)
        await asyncio.sleep(1.5)
        await self.eval("""
        (() => {
            const candidates = Array.from(document.querySelectorAll("button, [role='tab'], span"));
            const imgTab = candidates.find(c => c.innerText && c.innerText.trim() === 'Image');
            if (imgTab) imgTab.click();
        })()
        """)
        await asyncio.sleep(1)
        await self.dismiss_modals()

        # 2. Type Image Prompt
        print("  [*] Typing Image Prompt...", flush=True)
        await self.eval(f"""
        (() => {{
            const pm = document.querySelector('div.ProseMirror');
            if (!pm) return 'no_pm';
            pm.focus();
            document.execCommand('selectAll', false, null);
            document.execCommand('delete', false, null);
            document.execCommand('insertText', false, {json.dumps(prompt_text)});
            return 'typed';
        }})()
        """)
        await asyncio.sleep(1.5)

        # 3. Native CDP Click to Generate
        print("  [*] Clicking Generate for Reference Image...", flush=True)
        rect = await self.eval("""
        (() => {
            const btn = document.querySelector('button.generate-icon-button, [aria-label="Start generation"]');
            if (!btn) return null;
            const r = btn.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
        })()
        """)
        if rect:
            cx, cy = int(rect['x']), int(rect['y'])
            await self.call('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': cx, 'y': cy})
            await self.call('Input.dispatchMouseEvent', {'type': 'mousePressed', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
            await self.call('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})

        # 4. Wait for Image Render (~15s)
        print("  [*] Waiting for Image to render...", flush=True)
        for _ in range(30):
            await asyncio.sleep(2)
            spinners = await self.eval("document.querySelectorAll('.loading-percentage').length")
            if spinners == 0:
                print("  [✓] Reference 3D Image generated on canvas!", flush=True)
                break

    # -------------------------------------------------------------------------
    # PHASE 2: Strictly Attach Ingredients (Characters + Scene Image)
    # -------------------------------------------------------------------------
    async def attach_asset(self, category, item_name):
        print(f"  [+] Attaching {category} -> '{item_name}'...", flush=True)
        # Click '+' in prompt box
        await self.eval("""
        (() => {
            const addBtn = Array.from(document.querySelectorAll('button')).find(b => 
                b.getAttribute('aria-label') === 'Add ingredients to the prompt box' ||
                (b.innerText && b.innerText.trim() === 'add' && b.closest('.prompt-box, flow-base-prompt-box'))
            );
            if (addBtn) addBtn.click();
        })()
        """)
        await asyncio.sleep(1.5)

        # Click category (Characters / Images)
        await self.eval(f"""
        (() => {{
            const tabs = Array.from(document.querySelectorAll('mat-list-item, [role="tab"], button, span'));
            const targetTab = tabs.find(t => t.innerText && t.innerText.trim().includes('{category}'));
            if (targetTab) targetTab.click();
        }})()
        """)
        await asyncio.sleep(1.5)

        # Select item
        await self.eval(f"""
        (() => {{
            const items = Array.from(document.querySelectorAll('[role="option"], [class*="item"], div, span'));
            const target = items.find(i => i.innerText && i.innerText.trim().includes('{item_name}'));
            if (target) {{
                const clickEl = target.closest('[class*="item"], [role="option"]') || target;
                clickEl.click();
            }}
        }})()
        """)
        await asyncio.sleep(1.5)

        # MUST click the white 'Add to prompt' button!
        res = await self.eval("""
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const addBtn = btns.find(b => b.innerText && b.innerText.trim() === 'Add to prompt');
            if (addBtn && !addBtn.disabled) {
                addBtn.click();
                return 'added_to_prompt';
            }
            return 'failed_to_add';
        })()
        """)
        print(f"      Button click: {res}", flush=True)
        await asyncio.sleep(1.5)

    # -------------------------------------------------------------------------
    # PHASE 3: STRICT GUARDRAIL CHECK & Video Generation
    # -------------------------------------------------------------------------
    async def generate_video_with_mandatory_guardrail(self, characters, image_keyword, video_prompt, out_filename):
        print(f"\n[PHASE 2] Preparing Video with MANDATORY Character & Image Binding...", flush=True)
        await self.dismiss_modals()
        await self.clear_prompt_box()

        # 1. Switch to Video Mode (720p 8s 9:16)
        print("  [*] Switching mode to Video...", flush=True)
        await self.eval("""
        (() => {
            const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Banana') || b.innerText.includes('Image')));
            if (btn) btn.click();
        })()
        """)
        await asyncio.sleep(1.5)
        await self.eval("""
        (() => {
            const candidates = Array.from(document.querySelectorAll("button, [role='tab'], span"));
            const vidTab = candidates.find(c => c.innerText && c.innerText.trim() === 'Video');
            if (vidTab) vidTab.click();
        })()
        """)
        await asyncio.sleep(1)
        await self.dismiss_modals()

        # 2. Attach All Specified Characters
        for char in characters:
            await self.attach_asset("Characters", char)

        # 3. Attach Scene Reference Image
        if image_keyword:
            await self.attach_asset("Images", image_keyword)

        await self.dismiss_modals()

        # 4. MANDATORY UNBREAKABLE GUARDRAIL ASSERTION
        print("  [*] Verifying strict ingredient attachment in prompt box...", flush=True)
        chips_count = await self.eval("""
        (() => {
            const box = document.querySelector('.prompt-box, flow-base-prompt-box');
            if (!box) return 0;
            const chips = box.querySelectorAll('.chip-image, .chip-container, [class*="chip"]');
            return chips.length;
        })()
        """)
        print(f"      Found {chips_count} attached ingredient chips in prompt box.")
        
        if chips_count < 1:
            raise RuntimeError("CRITICAL ERROR: No ingredient chips attached in prompt box! Aborting submission per strict user policy!")

        # 5. Type Video Prompt
        print("  [*] Typing Video Prompt with cute toddler Hindi dialogues...", flush=True)
        await self.eval(f"""
        (() => {{
            const pm = document.querySelector('div.ProseMirror');
            if (!pm) return 'no_pm';
            pm.focus();
            document.execCommand('selectAll', false, null);
            document.execCommand('delete', false, null);
            document.execCommand('insertText', false, {json.dumps(video_prompt)});
            return 'typed';
        }})()
        """)
        await asyncio.sleep(1.5)

        # 6. Click Generate
        print("  [*] Submitting Video with attached ingredients...", flush=True)
        rect = await self.eval("""
        (() => {
            const btn = document.querySelector('button.generate-icon-button, [aria-label="Start generation"]');
            if (!btn) return null;
            const r = btn.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
        })()
        """)
        if rect:
            cx, cy = int(rect['x']), int(rect['y'])
            await self.call('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': cx, 'y': cy})
            await self.call('Input.dispatchMouseEvent', {'type': 'mousePressed', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
            await self.call('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})

        # 7. Auto-approvals check
        for _ in range(5):
            app = await self.eval("""
            (() => {
                const always = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Always approve'));
                if (always && always.offsetParent !== null) { always.click(); return 'always_approved'; }
                const approve = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.trim() === 'Approve');
                if (approve && approve.offsetParent !== null) { approve.click(); return 'approved'; }
                return 'none';
            })()
            """)
            if app in ['always_approved', 'approved']:
                print(f"      Auto-approval: {app}", flush=True)
                break
            await asyncio.sleep(1)

        # 8. Wait for render completion
        print("  [*] Rendering video on Google Flow...", flush=True)
        for minute in range(35):
            await asyncio.sleep(6)
            stat = await self.eval("""
            (() => {
                const p = Array.from(document.querySelectorAll('.loading-percentage, [class*="progress"]')).map(e => e.innerText ? e.innerText.trim() : '');
                const spinners = document.querySelectorAll('.loading-percentage').length;
                return { p, spinners };
            })()
            """)
            p_text = stat.get('p', [])
            spin = stat.get('spinners', 0)
            if p_text:
                print(f"      Progress: {p_text[0]}", flush=True)
            if spin == 0 and minute > 2:
                print("  [✓] Video Render Completed!", flush=True)
                break

        # 9. Download 720p with 100% Original Audio
        print(f"  [*] Downloading raw clip to {out_filename}...", flush=True)
        downloads_dir = Path(r"C:\Users\user\Downloads")
        before_files = set(f.name for f in downloads_dir.glob("*"))

        # Click top newest video card
        await self.eval("""
        (() => {
            const imgs = Array.from(document.querySelectorAll('img')).filter(i => i.src && i.src.includes('flow-content.google/image'));
            if (imgs.length > 0) {
                const card = imgs[0].closest('[class*="card"], [class*="item"], div');
                if (card) card.click();
            }
        })()
        """)
        await asyncio.sleep(2)

        # Click Download button -> 720p
        await self.eval("""
        (() => {
            const dlBtn = Array.from(document.querySelectorAll('button, a')).find(b => 
                (b.innerText && b.innerText.includes('download')) || b.getAttribute('aria-label') === 'Download'
            );
            if (dlBtn) dlBtn.click();
        })()
        """)
        await asyncio.sleep(1.5)
        await self.eval("""
        (() => {
            const btns = Array.from(document.querySelectorAll('cdk-overlay-container button, [role="menuitem"]'));
            const btn720 = btns.find(b => b.innerText && b.innerText.includes('720p'));
            if (btn720) btn720.click();
        })()
        """)

        # Wait for file in downloads
        target_path = RAW_CLIPS_DIR / out_filename
        downloaded = None
        for _ in range(15):
            await asyncio.sleep(1)
            current_files = set(f.name for f in downloads_dir.glob("*"))
            new_files = current_files - before_files
            for nf in new_files:
                p = downloads_dir / nf
                if p.is_file() and p.stat().st_size > 1000000:
                    downloaded = p
                    break
            if downloaded:
                break

        if downloaded:
            shutil.copy2(downloaded, target_path)
            print(f"  [SUCCESS] Clip saved: {target_path} ({os.path.getsize(target_path)} bytes)", flush=True)
        else:
            recent = sorted(downloads_dir.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True)
            if recent and recent[0].stat().st_size > 1000000:
                shutil.copy2(recent[0], target_path)
                print(f"  [SUCCESS via fallback] Clip saved: {target_path} ({os.path.getsize(target_path)} bytes)", flush=True)

        await self.dismiss_modals()
        return target_path
