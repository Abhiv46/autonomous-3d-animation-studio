import asyncio
import json
import os
import urllib.request
import websockets
from pathlib import Path

SAVE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips")
SAVE_DIR.mkdir(parents=True, exist_ok=True)
TARGET_FILE = SAVE_DIR / "ep23_lively_raw.mp4"

async def download_tile1():
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

        # Enable browser download
        print(f"[2] Enabling Page download behavior to {SAVE_DIR.resolve()}...", flush=True)
        await call("Browser.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": str(SAVE_DIR.resolve()),
            "eventsEnabled": True
        })
        await call("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": str(SAVE_DIR.resolve())
        })

        # Click tile 1 (the first card)
        print("[3] Clicking Tile 1 (Toddler and boy)...", flush=True)
        tile_pos = await eval_js("""
        (() => {
            const cards = Array.from(document.querySelectorAll("flow-card, [class*='card']"));
            // Find card with 'Toddler and boy' or the first one
            const target = cards.find(c => c.innerText && c.innerText.includes('Toddler and boy')) || cards[0];
            if (!target) return null;
            const r = target.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
        })()
        """)
        print(f"    Tile position: {tile_pos}", flush=True)
        if tile_pos:
            cx, cy = int(tile_pos["x"]), int(tile_pos["y"])
            await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": cx, "y": cy})
            await call("Input.dispatchMouseEvent", {"type": "mousePressed", "button": "left", "clickCount": 1, "x": cx, "y": cy})
            await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "button": "left", "clickCount": 1, "x": cx, "y": cy})
            await asyncio.sleep(2)

        # Take screenshot of open player
        shot = await call("Page.captureScreenshot", {"format": "png"})
        import base64
        with open(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\tile1_opened_player.png", "wb") as f:
            f.write(base64.b64decode(shot["data"]))

        # Find Download button in player
        print("[4] Locating Download button in player...", flush=True)
        dl_btn = await eval_js("""
        (() => {
            const btns = Array.from(document.querySelectorAll("button"));
            const dl = btns.find(b => 
                (b.innerText && b.innerText.trim().toLowerCase() === 'download') ||
                (b.getAttribute('aria-label') && b.getAttribute('aria-label').toLowerCase().includes('download'))
            );
            if (!dl) return null;
            const r = dl.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
        })()
        """)
        print(f"    Download button coords: {dl_btn}", flush=True)

        if dl_btn:
            dx, dy = int(dl_btn["x"]), int(dl_btn["y"])
            await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": dx, "y": dy})
            await call("Input.dispatchMouseEvent", {"type": "mousePressed", "button": "left", "clickCount": 1, "x": dx, "y": dy})
            await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "button": "left", "clickCount": 1, "x": dx, "y": dy})
            await asyncio.sleep(1.5)

            # Click 720p option in menu
            print("[5] Selecting '720p Original size'...", flush=True)
            p720 = await eval_js("""
            (() => {
                const items = Array.from(document.querySelectorAll("[role='menuitem'], button, div, span"));
                const target = items.find(i => i.innerText && i.innerText.includes('720p'));
                if (!target) return null;
                const r = target.getBoundingClientRect();
                return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
            })()
            """)
            print(f"    720p menu item coords: {p720}", flush=True)
            if p720:
                px, py = int(p720["x"]), int(p720["y"])
                await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": px, "y": py})
                await call("Input.dispatchMouseEvent", {"type": "mousePressed", "button": "left", "clickCount": 1, "x": px, "y": py})
                await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "button": "left", "clickCount": 1, "x": px, "y": py})
                print("    Dispatched click on 720p download option!", flush=True)

        # Wait for file to download
        print("[6] Monitoring download directory...", flush=True)
        for sec in range(25):
            await asyncio.sleep(1)
            # Check files in SAVE_DIR
            files = list(SAVE_DIR.glob("*.mp4"))
            # Find the newest downloaded file
            newest = max(files, key=os.path.getmtime) if files else None
            if newest and ("toddler" in newest.name.lower() or os.path.getmtime(newest) > time.time() - 30):
                print(f"[SUCCESS] Downloaded file found: {newest.name} ({newest.stat().st_size} bytes)")
                if newest != TARGET_FILE:
                    import shutil
                    shutil.copy2(newest, TARGET_FILE)
                break

if __name__ == "__main__":
    import time
    asyncio.run(download_tile1())
