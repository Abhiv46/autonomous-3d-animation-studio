import asyncio
import json
import urllib.request
import base64
import websockets

async def main():
    req = urllib.request.urlopen("http://127.0.0.1:9222/json")
    tabs = json.loads(req.read().decode())
    target = None
    for t in tabs:
        url = t.get("url", "")
        if "studio.youtube.com" in url and "k2JBp96Iqa4" in url:
            target = t
            break
    if not target:
        for t in tabs:
            if "studio.youtube.com" in t.get("url", ""):
                target = t
                break

    if not target:
        print("[-] Studio tab not found!")
        return

    ws_url = target["webSocketDebuggerUrl"]
    print(f"[+] Connecting to {ws_url}...")

    async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
        msg_id = 0
        async def send_cmd(method, params=None):
            nonlocal msg_id
            msg_id += 1
            payload = {"id": msg_id, "method": method}
            if params:
                payload["params"] = params
            await ws.send(json.dumps(payload))
            while True:
                raw = await ws.recv()
                data = json.loads(raw)
                if data.get("id") == msg_id:
                    return data

        # Dismiss hashtag autocomplete with Escape
        await send_cmd("Input.dispatchKeyEvent", {"type": "rawKeyDown", "windowsVirtualKeyCode": 27, "key": "Escape", "code": "Escape"})
        await send_cmd("Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 27, "key": "Escape", "code": "Escape"})
        await asyncio.sleep(0.5)

        # Check save button state and click it
        res = await send_cmd("Runtime.evaluate", {
            "expression": """(() => {
                const saveBtn = document.querySelector('ytcp-button#save-button button, button#save, #save-button');
                if (!saveBtn) return 'Button not found';
                const disabled = saveBtn.getAttribute('disabled') !== null || saveBtn.getAttribute('aria-disabled') === 'true';
                if (!disabled) {
                    saveBtn.click();
                    return 'Clicked save button!';
                }
                return 'Button disabled: already saved';
            })()""",
            "returnByValue": True
        })
        print("[+] Save click response:", res.get("result", {}).get("value"))

        await asyncio.sleep(3.0)

        # Take confirmation screenshot
        ss = await send_cmd("Page.captureScreenshot", {"format": "png"})
        img_data = base64.b64decode(ss["result"]["data"])
        out_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_color_final_saved_success.png"
        with open(out_path, "wb") as f:
            f.write(img_data)
        print(f"[SUCCESS] Saved screenshot to {out_path}!")

if __name__ == "__main__":
    asyncio.run(main())
