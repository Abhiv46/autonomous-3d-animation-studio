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

        # 1. Dismiss any open modal
        await call('Runtime.evaluate', {
            'expression': "(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()"
        })
        await asyncio.sleep(1)

        # 2. Clear prompt box
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const clearBtn = document.querySelector('button.clear-button, [aria-label*="Clear" i]');
                if (clearBtn) clearBtn.click();
                const pm = document.querySelector('div.ProseMirror');
                if (pm) {
                    pm.focus();
                    document.execCommand('selectAll', false, null);
                    document.execCommand('delete', false, null);
                }
            })()
            """
        })
        await asyncio.sleep(1)

        # 3. Click the '+' button (Add ingredients to the prompt box)
        print("[1] Clicking '+' (Add ingredients)...", flush=True)
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const addBtn = Array.from(document.querySelectorAll('button')).find(b => 
                    b.getAttribute('aria-label') === 'Add ingredients to the prompt box' ||
                    (b.innerText && b.innerText.trim() === 'add' && b.closest('.prompt-box, flow-base-prompt-box'))
                );
                if (addBtn) {
                    addBtn.click();
                    return 'clicked_add';
                }
                return 'add_not_found';
            })()
            """
        })
        await asyncio.sleep(1.5)

        # 4. Check menu and click 'Images'
        print("[2] Clicking 'Images' in menu...", flush=True)
        await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const items = Array.from(document.querySelectorAll('mat-list-item, [role="menuitem"], button, span'));
                const imgMenu = items.find(i => i.innerText && i.innerText.includes('Images'));
                if (imgMenu) {
                    imgMenu.click();
                    return 'clicked_images_menu';
                }
                return 'not_found';
            })()
            """
        })
        await asyncio.sleep(2)

        # 5. Look for available image tiles in the overlay
        tiles = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const overlay = document.querySelector('.cdk-overlay-container');
                if (!overlay) return [];
                const items = Array.from(overlay.querySelectorAll('[role="option"], [class*="item"], [class*="tile"], div:has(> img)')).map(el => ({
                    text: el.innerText ? el.innerText.trim() : '',
                    hasImg: !!el.querySelector('img'),
                    imgSrc: el.querySelector('img') ? el.querySelector('img').src.slice(0, 60) : ''
                }));
                return items.filter(x => x.text || x.hasImg).slice(0, 10);
            })()
            """,
            'returnByValue': True
        })
        print("Available Image Tiles in Overlay:", json.dumps(tiles.get('result', {}).get('value'), indent=2))

        # 6. Click the first image tile (our Scene 1 or Scene 2 3D image)
        click_tile = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const overlay = document.querySelector('.cdk-overlay-container');
                if (!overlay) return 'no_overlay';
                const firstTile = overlay.querySelector('img');
                if (firstTile) {
                    const card = firstTile.closest('[class*="item"], [class*="tile"], button, div') || firstTile;
                    card.click();
                    return 'clicked_first_image_tile';
                }
                return 'no_img_in_overlay';
            })()
            """,
            'returnByValue': True
        })
        print(f"Clicked image tile: {click_tile.get('result', {}).get('value')}", flush=True)
        await asyncio.sleep(2)

        # 7. Now check what is inside the prompt box! Is the thumbnail pill attached?
        prompt_box_state = await call('Runtime.evaluate', {
            'expression': """
            (() => {
                const box = document.querySelector('.prompt-box, flow-base-prompt-box');
                if (!box) return 'no_box';
                const imgs = Array.from(box.querySelectorAll('img')).map(i => ({
                    src: i.src.slice(0, 60),
                    w: i.width,
                    h: i.height,
                    className: i.className
                }));
                const pills = Array.from(box.querySelectorAll('[class*="pill"], [class*="chip"], [class*="ingredient"], [class*="media"]')).map(p => p.className);
                return {
                    imgsInPromptBox: imgs,
                    pills: pills,
                    boxText: box.innerText.slice(0, 150)
                };
            })()
            """,
            'returnByValue': True
        })
        print("Prompt Box State after attaching:", json.dumps(prompt_box_state.get('result', {}).get('value'), indent=2))

if __name__ == '__main__':
    asyncio.run(run())
