import asyncio
import json
import urllib.request
import websockets

async def run():
    req = urllib.request.urlopen('http://127.0.0.1:9222/json/list')
    tabs = json.loads(req.read().decode())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    print(f"Connecting to tab WS: {ws_url}", flush=True)
    
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

        # 1. Switch back to Video Mode
        print("[1] Opening Mode Menu...", flush=True)
        open_res = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const modeBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Banana') || b.innerText.includes('Image')));
                if (modeBtn) {
                    modeBtn.click();
                    return 'mode_clicked';
                }
                return 'not_found';
            })()
            """,
            'returnByValue': True
        })
        print(f"    Open mode menu: {open_res.get('result', {}).get('value')}", flush=True)
        await asyncio.sleep(1.5)
        
        # Click 'Video' option
        click_vid = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const candidates = Array.from(document.querySelectorAll("button, [role='tab'], [role='option'], span"));
                const vidTab = candidates.find(c => c.innerText && c.innerText.trim() === 'Video');
                if (vidTab) {
                    vidTab.click();
                    return 'video_clicked';
                }
                return 'not_found';
            })()
            """,
            'returnByValue': True
        })
        print(f"    Click Video option: {click_vid.get('result', {}).get('value')}", flush=True)
        await asyncio.sleep(1.5)
        
        # Dismiss any open popover with Escape
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true });
                document.dispatchEvent(esc);
            })()
            """
        })
        await asyncio.sleep(1)
        
        # 2. Click the '+' button in prompt box to add ingredients
        print("[2] Clicking '+' button to add ingredients...", flush=True)
        plus_res = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const plusBtn = Array.from(document.querySelectorAll('button')).find(b => b.getAttribute('aria-label') === 'Add ingredients to the prompt box' || (b.innerText && b.innerText.trim() === 'add'));
                if (plusBtn) {
                    plusBtn.click();
                    return 'plus_clicked';
                }
                return 'plus_not_found';
            })()
            """,
            'returnByValue': True
        })
        print(f"    Plus clicked: {plus_res.get('result', {}).get('value')}", flush=True)
        await asyncio.sleep(2)
        
        # Check what appears in open ingredient selector
        items = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const els = Array.from(document.querySelectorAll('[role=\"menuitem\"], [role=\"option\"], [class*=\"item\"], button, img'))
                    .map(el => ({
                        tag: el.tagName,
                        text: el.innerText ? el.innerText.trim() : '',
                        alt: el.alt || '',
                        aria: el.getAttribute('aria-label') || ''
                    }))
                    .filter(x => x.text || x.alt || x.aria);
                return els.slice(0, 30);
            })()
            """,
            'returnByValue': True
        })
        print("Ingredient Menu Items:", json.dumps(items.get('result', {}).get('value'), indent=2, ensure_ascii=True))

if __name__ == '__main__':
    asyncio.run(run())
