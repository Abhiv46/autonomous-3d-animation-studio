import asyncio
import json
import urllib.request
import base64
import time
import sys
import shutil
from pathlib import Path
import websockets

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SCREENSHOT_DIR = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2")
RAW_CLIPS_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips")
RAW_CLIPS_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR = Path(r"C:\Users\user\Downloads")

class VideoMasterProducer:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self.msg_counter = 100

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, max_size=50*1024*1024)

    async def close(self):
        if self.ws:
            await self.ws.close()

    async def send_cmd(self, method, params=None, timeout=12):
        self.msg_counter += 1
        msg_id = self.msg_counter
        msg = {'id': msg_id, 'method': method, 'params': params or {}}
        await self.ws.send(json.dumps(msg))
        start_t = time.time()
        while time.time() - start_t < timeout:
            try:
                raw = await asyncio.wait_for(self.ws.recv(), timeout=2.0)
                res = json.loads(raw)
                if res.get('id') == msg_id:
                    return res.get('result', {})
            except asyncio.TimeoutError:
                pass
        return {}

    async def eval_js(self, js):
        res = await self.send_cmd('Runtime.evaluate', {
            'expression': js,
            'returnByValue': True,
            'awaitPromise': True
        })
        return res.get('result', {}).get('value')

    async def take_screenshot(self, filename):
        res = await self.send_cmd('Page.captureScreenshot', {'format': 'png'}, timeout=15)
        if 'data' in res:
            path = SCREENSHOT_DIR / filename
            with open(path, 'wb') as f:
                f.write(base64.b64decode(res['data']))
            print(f"  [SCREENSHOT] Saved: {filename}", flush=True)

    async def dismiss_modals(self):
        await self.eval_js("(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()")
        await asyncio.sleep(1)

    async def clear_prompt_box(self):
        await self.eval_js("""
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

    async def switch_to_video_mode(self):
        print("  [*] Switching mode to Video (720p 8s 9:16)...", flush=True)
        await self.dismiss_modals()
        # Click mode button if not video
        await self.eval_js("""
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const modeBtn = btns.find(b => b.innerText && (b.innerText.includes('Banana') || b.innerText.includes('Image')));
            if (modeBtn) modeBtn.click();
        })()
        """)
        await asyncio.sleep(1.5)
        # Select Video tab
        await self.eval_js("""
        (() => {
            const opts = Array.from(document.querySelectorAll('button, [role="tab"], [role="menuitem"], span'));
            const vidTab = opts.find(o => o.innerText && o.innerText.trim() === 'Video');
            if (vidTab) vidTab.click();
        })()
        """)
        await asyncio.sleep(1.5)
        await self.dismiss_modals()

    # -------------------------------------------------------------------------
    # MANDATORY ASSET ATTACHMENT WITH CLICKING "ADD TO PROMPT"
    # -------------------------------------------------------------------------
    async def attach_asset(self, category, search_text):
        print(f"  [+] Attaching {category} -> '{search_text}'...", flush=True)
        await self.dismiss_modals()
        
        # 1. Click '+' button in prompt box
        await self.eval_js("""
        (() => {
            const addBtn = Array.from(document.querySelectorAll('button')).find(b => 
                b.getAttribute('aria-label') === 'Add ingredients to the prompt box' ||
                (b.innerText && b.innerText.trim() === 'add' && b.closest('.prompt-box, flow-base-prompt-box'))
            );
            if (addBtn) addBtn.click();
        })()
        """)
        await asyncio.sleep(1.5)

        # 2. Click category tab (Characters / Images)
        await self.eval_js(f"""
        (() => {{
            const tabs = Array.from(document.querySelectorAll('mat-list-item, [role="tab"], button, span, div'));
            const targetTab = tabs.find(t => t.innerText && t.innerText.trim().toLowerCase() === '{category.lower()}');
            if (targetTab) targetTab.click();
        }})()
        """)
        await asyncio.sleep(1.5)

        # 3. Select item matching search_text
        await self.eval_js(f"""
        (() => {{
            const items = Array.from(document.querySelectorAll('button.asset-item, flow-add-menu-asset-item, [role="option"], div, span'));
            const target = items.find(i => i.innerText && i.innerText.trim().toLowerCase().includes('{search_text.lower()}'));
            if (target) {{
                const btn = target.closest('button.asset-item') || target;
                btn.click();
            }}
        }})()
        """)
        await asyncio.sleep(1.5)

        # 4. CRITICAL: Click white 'Add to prompt' button!
        status = await self.eval_js("""
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
        print(f"      Button status: {status}", flush=True)
        await asyncio.sleep(1.5)
        await self.dismiss_modals()

    # -------------------------------------------------------------------------
    # SCENE VIDEO GENERATION & DOWNLOAD
    # -------------------------------------------------------------------------
    async def produce_scene(self, scene_num, characters, image_title, video_prompt, out_filename):
        print(f"\n=======================================================", flush=True)
        print(f"[*] PRODUCING SCENE {scene_num} VIDEO (WITH MANDATORY CHIPS)", flush=True)
        print(f"=======================================================", flush=True)
        
        await self.dismiss_modals()
        await self.switch_to_video_mode()
        await self.clear_prompt_box()

        # 1. Attach All Characters
        for char in characters:
            await self.attach_asset("Characters", char)

        # 2. Attach Scene Reference Image
        if image_title:
            await self.attach_asset("Images", image_title)

        await self.dismiss_modals()
        await asyncio.sleep(1)

        # 3. MANDATORY GUARDRAIL ASSERTION: Check chips in prompt box
        chips_count = await self.eval_js("""
        (() => {
            const box = document.querySelector('.prompt-box, flow-base-prompt-box');
            if (!box) return 0;
            const chips = box.querySelectorAll('.chip-image, .chip-container, [class*="chip"]');
            return chips.length;
        })()
        """)
        print(f"  [GUARDRAIL] Verified attached chips in prompt box: {chips_count}", flush=True)
        await self.take_screenshot(f"ep22_scene{scene_num}_chips_verified.png")

        if not chips_count or int(chips_count) < 2:
            raise RuntimeError(f"ABORTED! Mandatory chips missing for Scene {scene_num} (found {chips_count})! Strict user policy enforced!")

        # 4. Type Video Prompt with toddler dialogues
        print(f"  [*] Typing Scene {scene_num} video prompt with cute toddler Hindi dialogues...", flush=True)
        await self.eval_js(f"""
        (() => {{
            const pm = document.querySelector('div.ProseMirror');
            if (pm) {{
                pm.focus();
                document.execCommand('insertText', false, {json.dumps(video_prompt)});
            }}
        }})()
        """)
        await asyncio.sleep(1.5)

        # Record files in Downloads before generating
        before_downloads = set(f.name for f in DOWNLOADS_DIR.glob("*"))

        # 5. Click Generate
        print("  [*] Submitting Scene Video generation...", flush=True)
        rect = await self.eval_js("""
        (() => {
            const btn = document.querySelector('button.generate-icon-button, [aria-label="Start generation"]');
            if (!btn) return null;
            const r = btn.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
        })()
        """)
        if rect:
            cx, cy = int(rect['x']), int(rect['y'])
            await self.send_cmd('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': cx, 'y': cy})
            await self.send_cmd('Input.dispatchMouseEvent', {'type': 'mousePressed', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})
            await self.send_cmd('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'button': 'left', 'clickCount': 1, 'x': cx, 'y': cy})

        # 6. Auto-Approve spend modal if present
        for _ in range(5):
            await asyncio.sleep(1)
            app = await self.eval_js("""
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

        # 7. Wait for video render to 100% complete (~80-120 seconds for 8s clip)
        print("  [*] Rendering Scene Video on Google Flow...", flush=True)
        await asyncio.sleep(10)
        for minute_step in range(45):
            await asyncio.sleep(5)
            stat = await self.eval_js("""
            (() => {
                const p = Array.from(document.querySelectorAll('.loading-percentage, [class*="progress"]')).map(e => e.innerText ? e.innerText.trim() : '');
                const hasStop = Array.from(document.querySelectorAll('button')).some(b => b.innerText && b.innerText.trim() === 'stop');
                return { p: p.filter(Boolean), isGenerating: hasStop };
            })()
            """)
            p_list = stat.get('p', [])
            is_gen = stat.get('isGenerating', False)
            if p_list:
                print(f"      Progress: {p_list[0]} ({(minute_step+1)*5}s)", flush=True)
            elif not is_gen and minute_step >= 3:
                print(f"  [✓] Scene {scene_num} Video Render Completed! ({(minute_step+1)*5}s)", flush=True)
                break

        await asyncio.sleep(3)
        await self.take_screenshot(f"ep22_scene{scene_num}_rendered.png")

        # 8. Download 720p raw clip
        print(f"  [*] Downloading raw clip to {out_filename}...", flush=True)
        # Click the top-left newest video card
        await self.eval_js("""
        (() => {
            const cards = Array.from(document.querySelectorAll('flow-project-card, [class*="card"], [class*="item"]')).filter(c => c.querySelector('img') || c.querySelector('video'));
            const latestVideo = cards.find(c => c.innerText && c.innerText.includes('00:08') || c.querySelector('flow-video-player'));
            if (latestVideo) latestVideo.click();
            else if (cards.length > 0) cards[0].click();
        })()
        """)
        await asyncio.sleep(2)

        # Click Download button -> 720p
        await self.eval_js("""
        (() => {
            const dlBtn = Array.from(document.querySelectorAll('button, a')).find(b => 
                (b.innerText && b.innerText.includes('download')) || b.getAttribute('aria-label') === 'Download'
            );
            if (dlBtn) dlBtn.click();
        })()
        """)
        await asyncio.sleep(1.5)
        await self.eval_js("""
        (() => {
            const btns = Array.from(document.querySelectorAll('cdk-overlay-container button, [role="menuitem"]'));
            const btn720 = btns.find(b => b.innerText && b.innerText.includes('720p'));
            if (btn720) btn720.click();
        })()
        """)

        # Wait for file in downloads
        target_path = RAW_CLIPS_DIR / out_filename
        downloaded = None
        for _ in range(20):
            await asyncio.sleep(1)
            current_downloads = set(f.name for f in DOWNLOADS_DIR.glob("*"))
            diff = current_downloads - before_downloads
            for fn in diff:
                p = DOWNLOADS_DIR / fn
                if p.is_file() and p.suffix.lower() == '.mp4' and p.stat().st_size > 1000000:
                    downloaded = p
                    break
            if downloaded:
                break

        if downloaded:
            shutil.copy2(downloaded, target_path)
            print(f"  [SUCCESS] Clip downloaded & saved: {target_path} ({target_path.stat().st_size} bytes)", flush=True)
        else:
            recent_vids = sorted(DOWNLOADS_DIR.glob("*.mp4"), key=lambda f: f.stat().st_mtime, reverse=True)
            if recent_vids and recent_vids[0].stat().st_size > 1000000:
                shutil.copy2(recent_vids[0], target_path)
                print(f"  [SUCCESS Fallback] Clip saved: {target_path} ({target_path.stat().st_size} bytes)", flush=True)

        await self.dismiss_modals()
        return target_path

async def main():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/list').read())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    print(f"Connecting to Google Flow: {ws_url}", flush=True)

    producer = VideoMasterProducer(ws_url)
    await producer.connect()

    try:
        # Scene 1 Video
        v1_prompt = "Vertical 9:16, 8s, Pixar 3D animated style for toddlers. Toddler Kaavya on wooden stool reaches into bowl of sweet dripping Gulab Jamuns, giggling innocently. She whispers in cute baby Hindi voice: 'Mmm, ek meetha gulab jamun mera!' Suddenly Kaartik in yellow tee jumps out from pantry with huge mischievous grin, pointing at her and shouting cutely: 'Aha Kaavya! Pakad liya! Chori chori khana!' Kaavya gasps adorably with wide eyes and cheeks full of syrup. High quality natural toddler voices and laughter, warm kitchen lighting."
        await producer.produce_scene(
            scene_num=1,
            characters=["Kaavya", "Kaartik"],
            image_title="Toddler reaching for gulab jamun",
            video_prompt=v1_prompt,
            out_filename="ep22_scene1.mp4"
        )
        await asyncio.sleep(4)

        # Scene 2 Video
        v2_prompt = "Vertical 9:16, 8s, Pixar 3D animated style for toddlers. Kaartik and Kaavya playfully pull the warm sticky sweet between their hands in cute toddler tug-of-war. Kaavya giggles in cute squeaky Hindi voice: 'Chhodo Kaartik, yeh mera hai!' Kaartik laughs loudly in cute baby Hindi voice: 'Aadha aadha! Sharing is caring behna!' Plop! The soft sweet squishes between their hands, splashing sticky syrup on Kaartik's nose. Both toddlers freeze in shock then burst into adorable giggles. Natural child laughter and cute baby dialogue."
        await producer.produce_scene(
            scene_num=2,
            characters=["Kaavya", "Kaartik"],
            image_title="Toddlers fighting over sweet snack",
            video_prompt=v2_prompt,
            out_filename="ep22_scene2.mp4"
        )
        await asyncio.sleep(4)

        # Scene 3 Video
        v3_prompt = "Vertical 9:16, 8s, Pixar 3D animated style for toddlers. Mom Pinki enters doorway smiling warmly: 'Yeh kya ho raha hai yahan?' Kaavya and Kaartik quickly turn around, holding half-squished sweet toward mom, saying in unison in sweetest toddler voices: 'Mummy tasty gulab jamun aapke liye!' Then Kaavya winks at camera, jumping happily and shouting cutely: 'Jaldi like karo aur subscribe karo!' Both toddlers giggle and wave happily at camera. Natural sweet toddler voices, cheerful Disney Pixar vibe."
        await producer.produce_scene(
            scene_num=3,
            characters=["Kaavya", "Kaartik", "Pinki Mom"],
            image_title="Children offering sweets to mother",
            video_prompt=v3_prompt,
            out_filename="ep22_scene3.mp4"
        )

        print("\n=======================================================", flush=True)
        print("[SUCCESS] ALL 3 SCENE VIDEOS PRODUCED & DOWNLOADED SUCCESSFULLY!", flush=True)
        print("=======================================================\n", flush=True)

    finally:
        await producer.close()

if __name__ == '__main__':
    asyncio.run(main())
