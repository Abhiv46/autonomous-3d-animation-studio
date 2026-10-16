import asyncio
import json
import urllib.request
import websockets
import base64

async def fix_tags():
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read())
    first_tab = tabs[0]
    ws_url = first_tab["webSocketDebuggerUrl"]
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        msg_id = 1
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cid = msg_id
            await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get("id") == cid:
                    return resp.get("result", {})

        async def eval_js(js):
            res = await call("Runtime.evaluate", {"expression": js, "returnByValue": True, "awaitPromise": True})
            return res.get("result", {}).get("value")

        # Delete 3 old chips to bring character count under 500
        js_remove = """
        (() => {
            const chips = Array.from(document.querySelectorAll("ytcp-chip #delete-chip-icon, ytcp-chip ytcp-icon-button"));
            // remove first 3
            if (chips.length >= 3) {
                chips[0].click();
                chips[1].click();
                chips[2].click();
                return 'deleted_3_chips';
            }
            return 'chips_count_' + chips.length;
        })()
        """
        r_del = await eval_js(js_remove)
        print("Delete result:", r_del)
        await asyncio.sleep(1.5)

        # Save
        js_save = """
        (() => {
            const saveBtn = document.querySelector("#save-button, button[aria-label*='Save' i], ytcp-button#save");
            if (saveBtn) {
                saveBtn.click();
                return 'save_clicked';
            }
            const btns = Array.from(document.querySelectorAll("button"));
            const s = btns.find(b => b.innerText && b.innerText.trim() === 'Save');
            if (s) {
                s.click();
                return 'save_clicked_btn';
            }
            return 'no_save';
        })()
        """
        r_save = await eval_js(js_save)
        print("Save result:", r_save)
        await asyncio.sleep(4)

        # Proof
        await call("Page.enable")
        s_res = await call("Page.captureScreenshot", {"format": "png"})
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_bandar_seo_saved_perfect.png"
        with open(proof_path, "wb") as f:
            f.write(base64.b64decode(s_res["data"]))
        print("[+] Proof saved to:", proof_path)

if __name__ == "__main__":
    asyncio.run(fix_tags())
