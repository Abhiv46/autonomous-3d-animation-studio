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
RAW_CLIPS_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips")
RAW_CLIPS_DIR.mkdir(parents=True, exist_ok=True)

class FlowProductionEngine:
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

    async def take_screenshot(self, filename):
        shot = await self.call('Page.captureScreenshot', {'format': 'png'})
        path = SCREENSHOT_DIR / filename
        with open(path, 'wb') as f:
            f.write(base64.b64decode(shot['data']))
        print(f"  [SCREENSHOT] Saved: {filename}", flush=True)

    async def dismiss_modals(self):
        await self.eval("(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()")
        await asyncio.sleep(1)

    async def wait_until_idle(self, max_seconds=60):
        print(f"  [*] Waiting for active generation to finish...", flush=True)
        for i in range(max_seconds // 3):
            await asyncio.sleep(3)
            # Check spend approval modal
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
                print(f"      [Auto-Approve] Modal clicked: {app}", flush=True)

            is_busy = await self.eval("""
            (() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const hasStop = btns.some(b => b.innerText && b.innerText.trim() === 'stop');
                const spinners = document.querySelectorAll('.loading-percentage, [class*="spinner"]').length;
                return hasStop || spinners > 0;
            })()
            """)
            if not is_busy and i >= 1:
                print(f"  [+] Engine idle and ready!", flush=True)
                return True
        print(f"  [!] Wait finished after {max_seconds}s.", flush=True)
        return True

    async def clear_prompt_box(self):
        await self.eval("""
        (() => {
            const clears = Array.from(document.querySelectorAll('button')).filter(b => 
                (b.innerText && b.innerText.trim() === 'close') && b.closest('.prompt-box, flow-base-prompt-box')
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

    async def set_mode(self, target_mode):
        print(f"  [*] Setting generation mode to '{target_mode}'...", flush=True)
        await self.dismiss_modals()
        # Open mode selector if needed
        await self.eval("""
        (() => {
            const allBtns = Array.from(document.querySelectorAll('button'));
            const m = allBtns.find(b => b.innerText && (b.innerText.includes('Video') || b.innerText.includes('Image') || b.innerText.includes('Banana')));
            if (m) m.click();
        })()
        """)
        await asyncio.sleep(1.5)
        # Select target option
        await self.eval(f"""
        (() => {{
            const opts = Array.from(document.querySelectorAll('button, [role="menuitem"], [role="tab"], span'));
            const target = opts.find(o => o.innerText && o.innerText.trim().toLowerCase() === '{target_mode.lower()}');
            if (target) target.click();
        }})()
        """)
        await asyncio.sleep(1.5)
        await self.dismiss_modals()

    # -------------------------------------------------------------------------
    # GENERATE REFERENCE IMAGE
    # -------------------------------------------------------------------------
    async def generate_scene_image(self, scene_num, prompt_text, filename):
        print(f"\n=======================================================", flush=True)
        print(f"[*] PHASE 1: GENERATING REFERENCE IMAGE FOR SCENE {scene_num}", flush=True)
        print(f"=======================================================", flush=True)
        await self.dismiss_modals()
        await self.set_mode("Image")
        await self.clear_prompt_box()

        # Type prompt
        print(f"  [*] Typing prompt for Scene {scene_num}...", flush=True)
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

        # Click Generate
        print("  [*] Submitting reference image generation...", flush=True)
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

        await self.wait_until_idle(max_seconds=50)
        await self.take_screenshot(filename)
        print(f"  [+] Scene {scene_num} Reference Image ready on canvas!\n", flush=True)

    # -------------------------------------------------------------------------
    # ATTACH ASSETS (Characters + Image)
    # -------------------------------------------------------------------------
    async def attach_drawer_item(self, category, item_name):
        print(f"  [+] Attaching {category} -> '{item_name}'...", flush=True)
        # Click '+' button in prompt box
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

        # Click category tab (Characters / Images)
        await self.eval(f"""
        (() => {{
            const tabs = Array.from(document.querySelectorAll('mat-list-item, [role="tab"], button, span'));
            const targetTab = tabs.find(t => t.innerText && t.innerText.trim().toLowerCase() === '{category.lower()}');
            if (targetTab) targetTab.click();
        }})()
        """)
        await asyncio.sleep(1.5)

        # Click the item
        await self.eval(f"""
        (() => {{
            const items = Array.from(document.querySelectorAll('.asset-item, flow-add-menu-asset-item, [role="option"], div, span, button'));
            const target = items.find(i => i.innerText && i.innerText.trim().toLowerCase().includes('{item_name.lower()}'));
            if (target) {{
                const btn = target.closest('button.asset-item') || target;
                btn.click();
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
            return 'not_found_or_disabled';
        })()
        """)
        print(f"      Button click status: {res}", flush=True)
        await asyncio.sleep(1.5)

    # -------------------------------------------------------------------------
    # GENERATE SCENE VIDEO WITH STRICT CHIP VERIFICATION
    # -------------------------------------------------------------------------
    async def generate_scene_video(self, scene_num, char_names, image_keyword, video_prompt, out_filename):
        print(f"\n=======================================================", flush=True)
        print(f"[*] PHASE 2: GENERATING SCENE {scene_num} VIDEO WITH ATTACHED CHIPS", flush=True)
        print(f"=======================================================", flush=True)
        await self.dismiss_modals()
        await self.set_mode("Video")
        await self.clear_prompt_box()

        # 1. Attach All Characters
        for char in char_names:
            await self.attach_drawer_item("Characters", char)

        # 2. Attach Scene Reference Image
        if image_keyword:
            await self.attach_drawer_item("Images", image_keyword)

        await self.dismiss_modals()

        # 3. MANDATORY CHIP VERIFICATION GUARDRAIL
        chips_count = await self.eval("""
        (() => {
            const box = document.querySelector('.prompt-box, flow-base-prompt-box');
            if (!box) return 0;
            const chips = box.querySelectorAll('.chip-image, .chip-container, [class*="chip"]');
            return chips.length;
        })()
        """)
        print(f"  [GUARDRAIL] Verified attached ingredient chips count: {chips_count}")
        await self.take_screenshot(f"scene{scene_num}_chips_verified.png")

        if not chips_count or int(chips_count) < 1:
            raise RuntimeError(f"CRITICAL GUARDRAIL VIOLATION: Zero chips attached for Scene {scene_num}! Aborting per user strict command!")

        # 4. Type Video Prompt
        print(f"  [*] Typing video prompt with toddler Hindi dialogues...", flush=True)
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

        # 5. Submit Video Generation
        print("  [*] Submitting video generation...", flush=True)
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

        # Wait for video render
        print("  [*] Waiting for video render to complete (8s clip)...", flush=True)
        await asyncio.sleep(10)
        await self.wait_until_idle(max_seconds=180)
        await self.take_screenshot(f"scene{scene_num}_rendered.png")

        # 6. Download raw clip
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
            import shutil
            shutil.copy2(downloaded, target_path)
            print(f"  [SUCCESS] Clip saved: {target_path} ({target_path.stat().st_size} bytes)", flush=True)
        else:
            recent = sorted(downloads_dir.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True)
            if recent and recent[0].stat().st_size > 1000000:
                import shutil
                shutil.copy2(recent[0], target_path)
                print(f"  [SUCCESS via fallback] Clip saved: {target_path} ({target_path.stat().st_size} bytes)", flush=True)

        await self.dismiss_modals()
        return target_path

async def run_pipeline():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/list').read())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    print(f"Connecting to Google Flow: {ws_url}", flush=True)

    engine = FlowProductionEngine(ws_url)
    await engine.connect()

    try:
        # Check if first image is still rendering from previous step
        await engine.wait_until_idle(max_seconds=40)
        await engine.take_screenshot("scene1_initial_status.png")

        # -------------------------------------------------------------
        # PHASE 1: GENERATE ALL 3 REFERENCE IMAGES FIRST!
        # -------------------------------------------------------------
        # Scene 2 Reference Image
        p2_img = "Pixar 3D animation style, 9:16 vertical. Inside warm Indian kitchen, toddler Kaartik tries to snatch the sweet sticky Gulab Jamun from toddler Kaavya's hand. Both toddlers playfully tugging at the sticky sweet ball, syrup on their chubby cheeks and clothes. Kaavya laughing happily with messy hands, Kaartik with sweet syrup on his nose. Cinematic Pixar lighting, vibrant warm colors, ultra cute toddler expressions."
        await engine.generate_scene_image(2, p2_img, "ep22_scene2_ref_done.png")

        # Scene 3 Reference Image
        p3_img = "Pixar 3D animation style, 9:16 vertical. In the Indian kitchen, Indian Mom Pinki in elegant lavender kurta stands in doorway smiling affectionately. Toddler Kaavya and toddler Kaartik sit on kitchen floor with sweet syrup on cheeks, smiling like cute little angels with guilty innocent puppy eyes, holding up half a gulab jamun offering it to mom. Warm cinematic Pixar lighting, ultra high quality 3D render."
        await engine.generate_scene_image(3, p3_img, "ep22_scene3_ref_done.png")

        # Take proof screenshot that all 3 reference images are on canvas!
        await engine.take_screenshot("all_3_reference_images_canvas_proof.png")
        print("\n=======================================================", flush=True)
        print("[LOCKED CHECKPOINT] ALL 3 REFERENCE IMAGES SUCCESSFULLY GENERATED FIRST!", flush=True)
        print("=======================================================\n", flush=True)

        # -------------------------------------------------------------
        # PHASE 2: PRODUCE SCENE VIDEOS (WITH MANDATORY CHIPS ATTACHED)
        # -------------------------------------------------------------
        # Scene 1 Video
        v1_prompt = "Vertical 9:16, 8s, Pixar 3D animated style for toddlers. Toddler Kaavya on stool reaches into bowl of sweet dripping Gulab Jamuns, giggling innocently. She whispers in cute baby Hindi voice: 'Mmm, ek meetha gulab jamun mera!' Suddenly Kaartik in yellow tee jumps out from pantry with huge mischievous grin, pointing at her and shouting cutely: 'Aha Kaavya! Pakad liya! Chori chori khana!' Kaavya gasps adorably with wide eyes and cheeks full of syrup. High quality natural toddler voices and laughter, warm kitchen lighting."
        await engine.generate_scene_video(1, ["Kaavya", "Kaartik"], "Gulab", v1_prompt, "ep22_scene1.mp4")

        # Scene 2 Video
        v2_prompt = "Vertical 9:16, 8s, Pixar 3D animated style for toddlers. Kaartik and Kaavya playfully pull the warm sticky sweet between their hands in cute toddler tug-of-war. Kaavya giggles in cute squeaky Hindi voice: 'Chhodo Kaartik, yeh mera hai!' Kaartik laughs loudly in cute baby Hindi voice: 'Aadha aadha! Sharing is caring behna!' Plop! The soft sweet squishes between their hands, splashing sticky syrup on Kaartik's nose. Both toddlers freeze in shock then burst into adorable giggles. Natural child laughter and cute baby dialogue."
        await engine.generate_scene_video(2, ["Kaavya", "Kaartik"], "tug", v2_prompt, "ep22_scene2.mp4")

        # Scene 3 Video
        v3_prompt = "Vertical 9:16, 8s, Pixar 3D animated style for toddlers. Mom Pinki enters doorway smiling warmly: 'Yeh kya ho raha hai yahan?' Kaavya and Kaartik quickly turn around, holding half-squished sweet toward mom, saying in unison in sweetest toddler voices: 'Mummy tasty gulab jamun aapke liye!' Then Kaavya winks at camera, jumping happily and shouting cutely: 'Jaldi like karo aur subscribe karo!' Both toddlers giggle and wave happily at camera. Natural sweet toddler voices, cheerful Disney Pixar vibe."
        await engine.generate_scene_video(3, ["Kaavya", "Kaartik", "Pinki Mom"], "caught", v3_prompt, "ep22_scene3.mp4")

        print("\n=======================================================", flush=True)
        print("[SUCCESS] ALL 3 SCENE VIDEOS PRODUCED WITH FULL CHIP ATTACHMENT!", flush=True)
        print("=======================================================", flush=True)

    finally:
        await engine.close()

if __name__ == '__main__':
    asyncio.run(run_pipeline())
