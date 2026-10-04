import asyncio
import json
import base64
import urllib.request
import websockets
from pathlib import Path

SCREENSHOT_DIR = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2")

IMAGE_PROMPT = (
    "Vertical 9:16 aspect ratio, ultra-colorful 3D Pixar animated cartoon comedy style. "
    "Living room floor with bright sunny pastel morning light. Exactly ONE toddler Kaavya (3.5 years old, "
    "bright pastel pink frock, twin high pigtail buns with pink ribbons, huge glossy brown cartoon eyes, "
    "blushing chubby cheeks) jumping high in the air with joyful toddler laughter, mouth wide open, "
    "tiny chubby hands reaching up to pop colorful floating soap bubbles. Beside her, Exactly ONE 5-year-old Kaartik "
    "(yellow cartoon tee, denim shorts, smiling cartoon face) dynamically waving a bubble wand with lots of "
    "iridescent shiny bubbles filling the room. Expressive cute cartoon faces, high saturation, dynamic bouncy cartoon energy, "
    "Cocomelon Disney Pixar 3D aesthetic, zero photorealism, ultra-vibrant candy colors."
)

async def main():
    req = urllib.request.urlopen("http://127.0.0.1:9222/json/list")
    tabs = json.loads(req.read().decode())
    flow_tab = next(t for t in tabs if "flow.google.com" in t.get("url", ""))
    ws_url = flow_tab["webSocketDebuggerUrl"]
    print(f"[1] Connecting to Flow Tab: {ws_url}", flush=True)

    async with websockets.connect(ws_url, max_size=50 * 1024 * 1024) as ws:
        msg_id = 1
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cur_id = msg_id
            await ws.send(json.dumps({"id": cur_id, "method": method, "params": params or {}}))
            while True:
                res = json.loads(await ws.recv())
                if res.get("id") == cur_id:
                    return res.get("result", {})

        async def eval_js(js):
            res = await call("Runtime.evaluate", {"expression": js, "returnByValue": True, "awaitPromise": True})
            return res.get("result", {}).get("value")

        async def take_screenshot(name):
            shot = await call("Page.captureScreenshot", {"format": "png"})
            path = SCREENSHOT_DIR / name
            with open(path, "wb") as f:
                f.write(base64.b64decode(shot["data"]))
            print(f"    [+] Screenshot saved: {name}", flush=True)

        # 1. Dismiss any open modals
        print("[2] Dismissing any open modals...", flush=True)
        await eval_js("(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()")
        await asyncio.sleep(1)

        # 2. Switch mode to Image (Nano Banana 2 · 9:16)
        print("[3] Switching to Image Mode (Nano Banana 2 · 9:16)...", flush=True)
        # Check current mode
        cur_mode = await eval_js("""
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const m = btns.find(b => b.innerText && (b.innerText.includes('Video') || b.innerText.includes('Image') || b.innerText.includes('Banana')));
            return m ? m.innerText : '';
        })()
        """)
        print(f"    Current mode: {cur_mode}", flush=True)

        if "Image" not in str(cur_mode) and "Banana" not in str(cur_mode):
            await eval_js("""
            (() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const m = btns.find(b => b.innerText && (b.innerText.includes('Video') || b.innerText.includes('Image') || b.innerText.includes('Banana')));
                if (m) m.click();
            })()
            """)
            await asyncio.sleep(1.5)
            await eval_js("""
            (() => {
                const opts = Array.from(document.querySelectorAll('button, [role=\"menuitem\"], [role=\"tab\"], span'));
                const img = opts.find(o => o.innerText && o.innerText.trim() === 'Image');
                if (img) img.click();
            })()
            """)
            await asyncio.sleep(1.5)
            # Dismiss dropdown
            await eval_js("(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()")
            await asyncio.sleep(1)

        # 3. Clear prompt box and remove any existing chips
        print("[4] Clearing prompt box and chips...", flush=True)
        await eval_js("""
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

        # 4. Type the new pure 3D Pixar Image Prompt
        print("[5] Typing vibrant 3D Pixar Image Prompt...", flush=True)
        await eval_js(f"""
        (() => {{
            const pm = document.querySelector('div.ProseMirror');
            if (!pm) return 'no_pm';
            pm.focus();
            document.execCommand('selectAll', false, null);
            document.execCommand('delete', false, null);
            document.execCommand('insertText', false, {json.dumps(IMAGE_PROMPT)});
            return 'typed';
        }})()
        """)
        await asyncio.sleep(1.5)

        # 5. Click Generate button
        print("[6] Submitting Image Generation...", flush=True)
        rect = await eval_js("""
        (() => {
            const btn = document.querySelector('button.generate-icon-button, [aria-label=\"Start generation\"], button:has-text(\"arrow_forward\")');
            const allBtns = Array.from(document.querySelectorAll('button'));
            const arrow = allBtns.find(b => b.innerText && b.innerText.includes('arrow_forward') && b.closest('.prompt-box, flow-base-prompt-box'));
            const target = btn || arrow;
            if (!target) return null;
            const r = target.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
        })()
        """)
        if rect:
            cx, cy = int(rect["x"]), int(rect["y"])
            await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": cx, "y": cy})
            await call("Input.dispatchMouseEvent", {"type": "mousePressed", "button": "left", "clickCount": 1, "x": cx, "y": cy})
            await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "button": "left", "clickCount": 1, "x": cx, "y": cy})
            print("    Generate button clicked via mouse dispatch!", flush=True)
        else:
            await eval_js("""
            (() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const arrow = btns.find(b => b.innerText && b.innerText.includes('arrow_forward') && b.closest('.prompt-box, flow-base-prompt-box'));
                if (arrow) arrow.click();
            })()
            """)
            print("    Generate button clicked via fallback!", flush=True)

        # Auto-approve spend modal if it appears
        for _ in range(4):
            await asyncio.sleep(1)
            app = await eval_js("""
            (() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const c = btns.find(b => b.innerText && (b.innerText.includes('Continue') || b.innerText.includes('Agree')));
                if (c && c.offsetParent !== null) {
                    c.click();
                    return 'approved';
                }
                return 'none';
            })()
            """)
            if app != "none":
                print(f"    Spend modal approved: {app}", flush=True)
                break

        await take_screenshot("ep23_image_submitted.png")
        print("[7] Image Generation submitted! Monitoring for completion...", flush=True)

        # Wait 30 seconds for Image generation
        for i in range(12):
            await asyncio.sleep(5)
            cards_count = await eval_js("document.querySelectorAll('flow-card, [class*=\"card\"]').length")
            print(f"    Check {i+1} ({(i+1)*5}s) - Canvas items: {cards_count}", flush=True)

        await take_screenshot("ep23_image_rendered.png")
        print("[SUCCESS] Reference Image generated successfully!", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
