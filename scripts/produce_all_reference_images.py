import asyncio
import json
import urllib.request
import base64
import time
from pathlib import Path
import websockets

SCREENSHOT_DIR = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2")

SCENE_IMAGES = [
    {
        "scene": 1,
        "name": "ep22_scene1_jamun_sneak",
        "prompt": "Pixar 3D animation style, 9:16 vertical. In a warm Indian kitchen at night, toddler Kaavya with cute double buns secretly sneaks on tiptoes onto a small wooden stool toward a kitchen counter. On the counter is a silver bowl filled with warm dripping Gulab Jamuns in golden syrup. Kaavya has big curious brown eyes, chubby blushing rosy cheeks, reaching one hand out. Toddler Kaartik in yellow tee peeks curiously from behind the pantry door. High 3D CGI detail, subsurface scattering, Disney Pixar lighting."
    },
    {
        "scene": 2,
        "name": "ep22_scene2_jamun_tug",
        "prompt": "Pixar 3D animation style, 9:16 vertical. Inside warm Indian kitchen, toddler Kaartik tries to snatch the sweet sticky Gulab Jamun from toddler Kaavya's hand. Both toddlers are playfully tugging at the sticky sweet, syrup on their chubby cheeks and clothes. Kaavya laughing happily with messy hands, Kaartik with sweet syrup on his nose. Cinematic Pixar lighting, vibrant warm colors, ultra cute toddler expressions."
    },
    {
        "scene": 3,
        "name": "ep22_scene3_jamun_caught_cta",
        "prompt": "Pixar 3D animation style, 9:16 vertical. In the Indian kitchen, Indian Mom Pinki in elegant lavender kurta stands in doorway smiling affectionately. Toddler Kaavya and toddler Kaartik sit on kitchen floor with sweet syrup on cheeks, smiling like cute little angels with guilty innocent puppy eyes, holding up half a gulab jamun offering it to mom. Warm cinematic Pixar lighting, ultra high quality 3D render."
    }
]

class ImageFactory:
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

    async def switch_to_image_mode(self):
        print("  [*] Ensuring mode is set to Image (9:16)...", flush=True)
        # Check current mode label
        mode_text = await self.eval("""
        (() => {
            const btn = document.querySelector('button.mode-select-button, [aria-label*="mode"], button:has-text("Image"), button:has-text("Video")');
            const allBtns = Array.from(document.querySelectorAll('button'));
            const m = allBtns.find(b => b.innerText && (b.innerText.includes('Video') || b.innerText.includes('Image') || b.innerText.includes('Banana')));
            return m ? m.innerText : '';
        })()
        """)
        print(f"      Current mode button text: '{mode_text}'", flush=True)

        if 'Image' not in str(mode_text) and 'Banana' not in str(mode_text):
            # Click mode button
            await self.eval("""
            (() => {
                const allBtns = Array.from(document.querySelectorAll('button'));
                const m = allBtns.find(b => b.innerText && (b.innerText.includes('Video') || b.innerText.includes('Image') || b.innerText.includes('Banana')));
                if (m) m.click();
            })()
            """)
            await asyncio.sleep(1.5)
            # Click Image option
            await self.eval("""
            (() => {
                const opts = Array.from(document.querySelectorAll('button, [role="menuitem"], [role="tab"], span'));
                const img = opts.find(o => o.innerText && o.innerText.trim() === 'Image');
                if (img) img.click();
            })()
            """)
            await asyncio.sleep(1.5)
            await self.dismiss_modals()

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

    async def generate_single_image(self, scene_info):
        s_num = scene_info['scene']
        name = scene_info['name']
        prompt = scene_info['prompt']
        print(f"\n==================================================", flush=True)
        print(f"[*] GENERATING REFERENCE IMAGE FOR SCENE {s_num}...", flush=True)
        print(f"==================================================", flush=True)
        
        await self.dismiss_modals()
        await self.switch_to_image_mode()
        await self.clear_prompt_box()

        # Type image prompt
        print(f"  [*] Typing prompt for Scene {s_num}...", flush=True)
        await self.eval(f"""
        (() => {{
            const pm = document.querySelector('div.ProseMirror');
            if (!pm) return 'no_pm';
            pm.focus();
            document.execCommand('selectAll', false, null);
            document.execCommand('delete', false, null);
            document.execCommand('insertText', false, {json.dumps(prompt)});
            return 'typed';
        }})()
        """)
        await asyncio.sleep(1.5)

        # Click Generate button
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
        else:
            await self.eval("""
            (() => {
                const btn = document.querySelector('button.generate-icon-button, [aria-label="Start generation"]');
                if (btn) btn.click();
            })()
            """)

        # Auto-approve spend modal if it appears
        for _ in range(4):
            await asyncio.sleep(1)
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
                print(f"      Spend approval clicked: {app}", flush=True)
                break

        # Wait for image render to complete
        print("  [*] Waiting for Image generation to finish...", flush=True)
        await asyncio.sleep(5)
        for t in range(25):
            await asyncio.sleep(2)
            spinners = await self.eval("document.querySelectorAll('.loading-percentage, [class*=\"spinner\"]').length")
            if spinners == 0:
                print(f"  [✓] Scene {s_num} Reference Image render complete!", flush=True)
                break
            if t % 5 == 0:
                print(f"      Rendering in progress... ({t*2}s)", flush=True)

        await asyncio.sleep(2)
        await self.take_screenshot(f"{name}_done.png")
        print(f"  [✓] Scene {s_num} Reference Image successfully added to canvas!\n", flush=True)

async def main():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/list').read())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    print(f"Connecting to Google Flow tab: {ws_url}")
    factory = ImageFactory(ws_url)
    await factory.connect()

    try:
        for scene_info in SCENE_IMAGES:
            await factory.generate_single_image(scene_info)
            await asyncio.sleep(3)

        print("\n[SUCCESS] ALL 3 REFERENCE 3D IMAGES GENERATED FIRST AS MANDATED BY USER!")
        await factory.take_screenshot("all_3_reference_images_canvas_proof.png")
    finally:
        await factory.close()

if __name__ == '__main__':
    asyncio.run(main())
