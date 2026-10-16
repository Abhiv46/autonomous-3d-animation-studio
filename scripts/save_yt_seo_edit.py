import asyncio
import json
import urllib.request
import websockets
import base64

YT_TITLE = "Mummy Ka Jhumka Kisne Chupaya? 😱✨ Kaavya Ki Cutest Shararat! 😂🧸 #TheNaughtyDuo #shorts"

YT_DESC = """Mummy tayyar ho rahi thi aur achanak unka pyara gold jhumka gayab ho gaya! 😱💍
Mummy ne pure kamre me dhoondha, Kaartik bhaiyya bhi pareshan ho gaye...
Lekin ruko! Kaavya ne jhumka kahan pehnaya tha? Apne cute Teddy Bear ke kaan me! 😂🧸✨
Dekhiye Kaavya aur Kaartik ki sabse adorable family comedy story! 🥰❤️

💬 Sawaal: Kya aapne bhi bachpan me Mummy ki jewellery ya makeup se khilone sajaye hain? Comment me batayein! 👇

🔔 Aise hi funny aur cute 3D family cartoons ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 💖

#shorts #TheNaughtyDuo #KaavyaAndKaartik #MummyKaJhumka #TeddyBear #FunnyShorts #HindiCartoon #3DAnimation #CartoonStories #SiblingsComedy #KidsAnimation #ViralShorts #Trending"""

YT_TAGS = [
    "The Naughty Duo", "TheNaughtyDuo", "Kaartik and Kaavya", "mummy ka jhumka",
    "teddy bear prank", "hindi cartoon", "3d animation hindi", "kids cartoon funny",
    "siblings comedy", "funny hindi stories", "cartoon video hindi", "shorts", "viral shorts"
]

async def update_seo():
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read())
    edit_tab = next((t for t in tabs if "video/P3y5NiV-pG4/edit" in t.get("url", "")), None)
    ws_url = edit_tab["webSocketDebuggerUrl"]
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

        # 1. Fill Title
        print("[1] Filling Title...")
        js_title = f"""
        (() => {{
            const titleBox = document.querySelector("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox, #title-textarea #textbox");
            if (titleBox) {{
                titleBox.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, {json.dumps(YT_TITLE[:100])});
                titleBox.dispatchEvent(new Event('input', {{ bubbles: true }}));
                return 'title_updated';
            }}
            return 'no_title_box';
        }})()
        """
        res_t = await eval_js(js_title)
        print("    Title:", res_t)
        await asyncio.sleep(1)

        # 2. Fill Description
        print("[2] Filling Description...")
        js_desc = f"""
        (() => {{
            const descBox = document.querySelector("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox, #description-textarea #textbox");
            if (descBox) {{
                descBox.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, {json.dumps(YT_DESC)});
                descBox.dispatchEvent(new Event('input', {{ bubbles: true }}));
                return 'desc_updated';
            }}
            return 'no_desc_box';
        }})()
        """
        res_d = await eval_js(js_desc)
        print("    Desc:", res_d)
        await asyncio.sleep(1)

        # 3. Expand Show More
        print("[3] Expanding Show more...")
        js_more = """
        (() => {
            const btn = document.querySelector("#toggle-button, button[aria-label*='Show more' i]");
            if (btn) {
                btn.click();
                return 'clicked_more';
            }
            return 'no_more';
        })()
        """
        res_m = await eval_js(js_more)
        print("    Show more:", res_m)
        await asyncio.sleep(1.5)

        # 4. Fill Tags
        print("[4] Filling Tags...")
        tags_str = ", ".join(YT_TAGS) + ","
        js_tags = f"""
        (() => {{
            const tagsInput = document.querySelector("input[aria-label*='Tag' i], input[placeholder*='tag' i], #tags-container input");
            if (tagsInput) {{
                tagsInput.focus();
                document.execCommand('insertText', false, {json.dumps(tags_str)});
                tagsInput.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', keyCode: 13, bubbles: true }}));
                return 'tags_added';
            }}
            return 'no_tags_input';
        }})()
        """
        res_tags = await eval_js(js_tags)
        print("    Tags:", res_tags)
        await asyncio.sleep(1.5)

        # 5. Click Save button
        print("[5] Clicking Save button...")
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
            return 'no_save_btn';
        })()
        """
        res_s = await eval_js(js_save)
        print("    Save click:", res_s)
        await asyncio.sleep(4)

        # 6. Capture screenshot
        await call("Page.enable")
        s_res = await call("Page.captureScreenshot", {"format": "png"})
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_seo_saved_proof.png"
        with open(proof_path, "wb") as f:
            f.write(base64.b64decode(s_res["data"]))
        print("[+] Saved proof screenshot to:", proof_path)

if __name__ == "__main__":
    asyncio.run(update_seo())
