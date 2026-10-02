import asyncio
import json
import urllib.request
import websockets

async def check():
    req = urllib.request.urlopen('http://127.0.0.1:9222/json/list')
    tabs = json.loads(req.read().decode())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
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

        # Click '+' in prompt box
        print("[1] Clicking '+' button...", flush=True)
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const addBtn = Array.from(document.querySelectorAll('button')).find(b => 
                    b.getAttribute('aria-label') === 'Add ingredients to the prompt box' ||
                    (b.innerText && b.innerText.trim() === 'add' && b.closest('.prompt-box, flow-base-prompt-box'))
                );
                if (addBtn) addBtn.click();
            })()
            """
        })
        await asyncio.sleep(1.5)

        # Click 'Characters' in menu
        print("[2] Clicking 'Characters'...", flush=True)
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const items = Array.from(document.querySelectorAll('mat-list-item, [role="menuitem"], button, span'));
                const charMenu = items.find(i => i.innerText && i.innerText.includes('Characters'));
                if (charMenu) charMenu.click();
            })()
            """
        })
        await asyncio.sleep(1.5)

        # List character items in overlay
        chars = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const overlay = document.querySelector('.cdk-overlay-container');
                if (!overlay) return [];
                const items = Array.from(overlay.querySelectorAll('[role="option"], [class*="item"], button, div:has(> img)')).map(el => ({
                    text: el.innerText ? el.innerText.trim() : '',
                    imgSrc: el.querySelector('img') ? el.querySelector('img').src.slice(0, 50) : ''
                }));
                return items.filter(x => x.text).slice(0, 10);
            })()
            """,
            'returnByValue': True
        })
        print("Characters found:", json.dumps(chars.get('result', {}).get('value'), indent=2))

        # Click Kaavya
        click_k = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const overlay = document.querySelector('.cdk-overlay-container');
                if (!overlay) return 'no_overlay';
                const items = Array.from(overlay.querySelectorAll('[role="option"], [class*="item"], button, div'));
                const kaavya = items.find(i => i.innerText && i.innerText.includes('Kaavya'));
                if (kaavya) { kaavya.click(); return 'clicked_kaavya'; }
                return 'kaavya_not_found';
            })()
            """,
            'returnByValue': True
        })
        print("Click Kaavya:", click_k.get('result', {}).get('value'))
        await asyncio.sleep(1.5)

        # Check prompt box state
        prompt_box_state = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const box = document.querySelector('.prompt-box, flow-base-prompt-box');
                const pills = box ? Array.from(box.querySelectorAll('[class*="chip"], [class*="ingredient"], [class*="tag"]')).map(p => p.innerText.trim()) : [];
                return { pills, boxText: box ? box.innerText.slice(0, 150) : '' };
            })()
            """,
            'returnByValue': True
        })
        print("Prompt Box State after adding character:", json.dumps(prompt_box_state.get('result', {}).get('value'), indent=2))

if __name__ == '__main__':
    asyncio.run(check())
