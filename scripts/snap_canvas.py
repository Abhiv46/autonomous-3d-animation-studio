import asyncio
import json
import urllib.request
import base64
from pathlib import Path
import websockets

SCREENSHOT_DIR = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2")

async def snap():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/list').read())
    flow_tab = next(t for t in tabs if 'flow.google.com' in t.get('url', ''))
    ws_url = flow_tab['webSocketDebuggerUrl']
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        msg = {'id': 1, 'method': 'Page.captureScreenshot', 'params': {'format': 'png'}}
        await ws.send(json.dumps(msg))
        res = json.loads(await ws.recv())
        with open(SCREENSHOT_DIR / 'canvas_current_state.png', 'wb') as f:
            f.write(base64.b64decode(res['result']['data']))
        print('Screenshot saved!')

if __name__ == '__main__':
    asyncio.run(snap())
