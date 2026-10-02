import asyncio
import json
import base64
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

        # 1. Clear everything in prompt box first
        print("[1] Resetting prompt box...", flush=True)
        await call('Runtime.evaluate', {
            'expression': """
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
            """
        })
        await asyncio.sleep(1)

        # 2. Function to add an ingredient from the asset drawer
        async def attach_asset(category, item_name):
            print(f"[*] Attaching {category} -> '{item_name}'...", flush=True)
            # Click '+' in prompt box
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

            # Click category in sidebar if needed (Characters or Images)
            await call('Runtime.evaluate', {
                'expression': f"""
                (() => {{
                    const tabs = Array.from(document.querySelectorAll('mat-list-item, [role="tab"], button, span'));
                    const targetTab = tabs.find(t => t.innerText && t.innerText.trim().includes('{category}'));
                    if (targetTab) targetTab.click();
                }})()
                """
            })
            await asyncio.sleep(1.5)

            # Click the target item in the list
            await call('Runtime.evaluate', {
                'expression': f"""
                (() => {{
                    const items = Array.from(document.querySelectorAll('[role="option"], [class*="item"], div, span'));
                    const target = items.find(i => i.innerText && i.innerText.trim().includes('{item_name}'));
                    if (target) {{
                        const clickEl = target.closest('[class*="item"], [role="option"]') || target;
                        clickEl.click();
                    }}
                }})()
                """
            })
            await asyncio.sleep(1.5)

            # Click the big white 'Add to prompt' button!
            click_add = await call('Runtime.evaluate', {
                'expression': """
                (() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    const addBtn = btns.find(b => b.innerText && b.innerText.trim() === 'Add to prompt');
                    if (addBtn && !addBtn.disabled) {
                        addBtn.click();
                        return 'clicked_add_to_prompt';
                    }
                    return 'add_btn_not_found_or_disabled';
                })()
                """,
                'returnByValue': True
            })
            print(f"    Add to prompt: {click_add.get('result', {}).get('value')}", flush=True)
            await asyncio.sleep(1.5)

        # Attach Kaavya Character
        await attach_asset("Characters", "Kaavya")
        # Attach Kaartik Character
        await attach_asset("Characters", "Kaartik")
        # Attach Scene Image
        await attach_asset("Images", "face mask")

        # Dismiss any open drawer
        await call('Runtime.evaluate', {
            'expression': "(() => { const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }); document.dispatchEvent(esc); })()"
        })
        await asyncio.sleep(1)

        # Capture screenshot of prompt box with all ingredients attached
        await call('Page.enable')
        ss = await call('Page.captureScreenshot', {'format': 'png'})
        if 'data' in ss:
            ss_path = r'C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\prompt_box_with_characters_and_image.png'
            with open(ss_path, 'wb') as f:
                f.write(base64.b64decode(ss['data']))
            print(f"[✓] Screenshot saved: {ss_path}", flush=True)

if __name__ == '__main__':
    asyncio.run(run())
