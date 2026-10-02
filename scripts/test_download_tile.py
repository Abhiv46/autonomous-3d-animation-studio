import asyncio
import json
import urllib.request
import base64
from pathlib import Path
import websockets

SCREENSHOT_DIR = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2")

async def click_tile():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/list').read())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        msg_id = 0
        async def send(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cur_id = msg_id
            await ws.send(json.dumps({'id': cur_id, 'method': method, 'params': params or {}}))
            while True:
                res = json.loads(await ws.recv())
                if res.get('id') == cur_id:
                    return res.get('result', {})

        # Click the first tile in tile-row
        print('Clicking Tile 1...')
        await send('Runtime.evaluate', {
            'expression': """
            (() => {
                const row = document.querySelector('.tile-row.virtual-item-container');
                if (!row) return 'no row';
                const firstChild = row.children[0];
                if (firstChild) {
                    firstChild.click();
                    return 'clicked first tile: ' + firstChild.className;
                }
                return 'no child';
            })()
            """
        })
        await asyncio.sleep(2)

        # Take screenshot of what opened
        shot = await send('Page.captureScreenshot', {'format': 'png'})
        with open(SCREENSHOT_DIR / 'tile1_opened.png', 'wb') as f:
            f.write(base64.b64decode(shot['data']))
        print('Screenshot saved: tile1_opened.png')

        # Check for download button or player
        res = await send('Runtime.evaluate', {
            'expression': """
            (() => {
                const btns = Array.from(document.querySelectorAll('button, a')).map(b => ({
                    text: b.innerText.trim(),
                    aria: b.getAttribute('aria-label'),
                    class: b.className
                })).filter(b => b.text || b.aria);
                return btns.slice(0, 30);
            })()
            """,
            'returnByValue': True
        })
        print('Buttons visible:', json.dumps(res.get('result', {}).get('value', []), indent=2))

if __name__ == '__main__':
    asyncio.run(click_tile())
