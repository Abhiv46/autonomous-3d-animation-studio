import asyncio
import json
import base64
import urllib.request
import websockets

async def main():
    req = urllib.request.urlopen("http://127.0.0.1:9222/json/list")
    tabs = json.loads(req.read().decode())
    yt_tab = None
    for t in tabs:
        if "studio.youtube.com" in t.get("url", ""):
            yt_tab = t
            break
            
    if not yt_tab:
        print("[!] YouTube tab not found!")
        return
        
    ws_url = yt_tab["webSocketDebuggerUrl"]
    print(f"[+] Connecting to: {ws_url}", flush=True)
    
    async with websockets.connect(ws_url, max_size=50*1024*1024, ping_interval=None) as ws:
        msg_id = 0
        
        async def send_cmd(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cur_id = msg_id
            payload = {"id": cur_id, "method": method, "params": params or {}}
            await ws.send(json.dumps(payload))
            while True:
                resp = await ws.recv()
                data = json.loads(resp)
                if data.get("id") == cur_id:
                    return data.get("result", {})
                    
        print("[+] Enabling domains...", flush=True)
        await send_cmd("Page.enable")
        await send_cmd("Runtime.enable")
        print("[+] Domains enabled!", flush=True)
        
        # 1. Take initial screenshot
        print("[+] Capturing screenshot...", flush=True)
        ss = await send_cmd("Page.captureScreenshot", {"format": "png"})
        if "data" in ss:
            with open(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_dialog_live_cdp.png", "wb") as f:
                f.write(base64.b64decode(ss["data"]))
            print("[+] Initial screenshot saved!", flush=True)
            
        # 2. Step through dialog
        for step in range(5):
            eval_res = await send_cmd("Runtime.evaluate", {
                "expression": """
                (() => {
                    const dialog = document.querySelector('ytcp-uploads-dialog');
                    if (!dialog) return { error: 'no dialog' };
                    
                    // Click not made for kids
                    const notKids = dialog.querySelector("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']");
                    let notKidsClicked = false;
                    if (notKids) {
                        notKids.click();
                        notKidsClicked = true;
                    }
                    
                    // Click Next button
                    const nextBtn = dialog.querySelector("#next-button, ytcp-button#next-button, button[aria-label='Next']");
                    let nextClicked = false;
                    if (nextBtn && nextBtn.offsetParent !== null && !nextBtn.hasAttribute('disabled')) {
                        nextBtn.click();
                        nextClicked = true;
                    }
                    
                    // Click Public
                    const pub = dialog.querySelector("tp-yt-paper-radio-button[name='PUBLIC']");
                    let pubClicked = false;
                    if (pub) {
                        pub.click();
                        pubClicked = true;
                    }
                    
                    // Click Done / Publish / Save
                    const doneBtn = dialog.querySelector("#done-button, ytcp-button#done-button, button[aria-label='Publish'], button[aria-label='Save']");
                    let doneClicked = false;
                    if (doneBtn && doneBtn.offsetParent !== null && !doneBtn.hasAttribute('disabled')) {
                        doneBtn.click();
                        doneClicked = true;
                    }
                    
                    // Click Publish Anyway if exists
                    const anywayBtn = document.querySelector("ytcp-button#publish-button, button:has-text('Publish anyway')");
                    let anywayClicked = false;
                    if (anywayBtn && anywayBtn.offsetParent !== null) {
                        anywayBtn.click();
                        anywayClicked = true;
                    }
                    
                    return {
                        step: """ + str(step) + """,
                        notKidsClicked,
                        nextClicked,
                        pubClicked,
                        doneClicked,
                        anywayClicked
                    };
                })()
                """,
                "returnByValue": True
            })
            val = eval_res.get("result", {}).get("value", {})
            print(f"Step {step+1} result: {val}", flush=True)
            await asyncio.sleep(2)
            
        # Final screenshot
        ss_final = await send_cmd("Page.captureScreenshot", {"format": "png"})
        if "data" in ss_final:
            with open(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_original_published_proof.png", "wb") as f:
                f.write(base64.b64decode(ss_final["data"]))
            print("[SUCCESS] Final screenshot saved!", flush=True)

asyncio.run(main())
