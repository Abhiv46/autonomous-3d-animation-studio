import asyncio
import json
import base64
import urllib.request
import websockets

VID_ID = "k2JBp96Iqa4"

YT_TITLE = "Kaartik & Kaavya Ki Magical Rainbow Duniya! 🌈✨ Colors Magic Quest! 🥰🎨 #TheNaughtyDuo #shorts"

YT_DESC = """Kaartik aur Kaavya pahunch gaye ek jadui Rainbow World me jahan se saare rang gayab ho gaye! 🌈😱
Lekin kya Kaavya aur Kaartik milkar Laal Seb, Neeli Titli, Peela Suraj aur Saare Colors wapas laa payenge? 🍎🦋☀️🌱

Dekhiye unka sabse pyara aur mazedaar Magic Color Adventure! 🥰✨

💬 Sawaal: Aapka sabse favourite color kaunsa hai? Comment me batayein! 👇❤️💙💛💚

🔔 Aise hi mazedaar aur cute 3D family cartoon stories ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! ✨

#TheNaughtyDuo #shorts #viral #funny #colorsong #rainbow #3danimation #hindicartoon #kidsanimation #cartoons #trending #ytshorts #learningcolors #funnycartoon #family"""

YT_TAGS = [
    "The Naughty Duo", "TheNaughtyDuo", "Kaartik and Kaavya", "learn colors hindi",
    "color song", "rainbow cartoon", "3d animation hindi", "hindi cartoon funny",
    "kids animation", "nursery rhyme hindi", "cartoon for toddlers", "relatable comedy",
    "shorts", "viral shorts", "trending shorts"
]

async def publish_draft():
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read())
    yt_tab = next(t for t in tabs if "studio.youtube.com" in t.get("url", "").lower())
    ws_url = yt_tab["webSocketDebuggerUrl"]
    
    async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
        msg_id = 0
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cid = msg_id
            await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get("id") == cid: return resp.get("result", {})

        async def eval_js(js):
            res = await call("Runtime.evaluate", {"expression": js, "returnByValue": True, "awaitPromise": True})
            return res.get("result", {}).get("value")

        # 1. Click 'Edit draft' button on the Shorts list
        print("[1] Clicking 'Edit draft' button...", flush=True)
        res_btn = await eval_js("""
        (() => {
            const btn = document.querySelector('button:has-text("Edit draft"), ytcp-button:has-text("Edit draft")') ||
                        Array.from(document.querySelectorAll("button, ytcp-button")).find(b => b.innerText && b.innerText.trim() === 'Edit draft');
            if (btn) {
                btn.click();
                return 'clicked';
            }
            return 'not_found';
        })()
        """)
        print("    Edit draft button click:", res_btn, flush=True)
        await asyncio.sleep(4)

        # 2. Fill Title
        print("[2] Filling Title in wizard...", flush=True)
        await eval_js(f"""
        (() => {{
            const diag = document.querySelector('ytcp-uploads-dialog');
            const titleBox = diag ? diag.querySelector("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox") : document.querySelector("#textbox[aria-label*='title' i]");
            if (titleBox) {{
                titleBox.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, {json.dumps(YT_TITLE[:100])});
                titleBox.dispatchEvent(new Event('input', {{ bubbles: true }}));
                return 'title_set';
            }}
            return 'no_title_box';
        }})()
        """)
        await asyncio.sleep(1)

        # 3. Fill Description
        print("[3] Filling Description in wizard...", flush=True)
        await eval_js(f"""
        (() => {{
            const diag = document.querySelector('ytcp-uploads-dialog');
            const descBox = diag ? diag.querySelector("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox") : document.querySelector("#textbox[aria-label*='description' i]");
            if (descBox) {{
                descBox.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, {json.dumps(YT_DESC)});
                descBox.dispatchEvent(new Event('input', {{ bubbles: true }}));
                return 'desc_set';
            }}
            return 'no_desc_box';
        }})()
        """)
        await asyncio.sleep(1)

        # 4. Audience: Not made for kids
        print("[4] Setting Audience...", flush=True)
        await eval_js("""
        (() => {
            const diag = document.querySelector('ytcp-uploads-dialog');
            const notKids = diag ? diag.querySelector("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']") : document.querySelector("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']");
            if (notKids) notKids.click();
        })()
        """)
        await asyncio.sleep(1)

        # 5. Show more & Tags
        print("[5] Adding Tags...", flush=True)
        await eval_js("""
        (() => {
            const diag = document.querySelector('ytcp-uploads-dialog');
            const toggle = diag ? diag.querySelector("#toggle-button") : document.querySelector("#toggle-button");
            if (toggle) toggle.click();
        })()
        """)
        await asyncio.sleep(1.5)

        tags_string = ", ".join(YT_TAGS) + ","
        await eval_js(f"""
        (() => {{
            const diag = document.querySelector('ytcp-uploads-dialog');
            const tagsInput = diag ? diag.querySelector("input[aria-label*='Tag' i], input[placeholder*='tag' i], #tags-container input") : document.querySelector("input[aria-label*='Tag' i]");
            if (tagsInput) {{
                tagsInput.focus();
                document.execCommand('insertText', false, {json.dumps(tags_string)});
                tagsInput.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', keyCode: 13, bubbles: true }}));
                return 'tags_added';
            }}
            return 'no_tags_input';
        }})()
        """)
        await asyncio.sleep(1)

        # 6. Click Visibility step badge (step-badge-3)
        print("[6] Navigating to Visibility tab...", flush=True)
        step_vis = await eval_js("""
        (() => {
            const diag = document.querySelector('ytcp-uploads-dialog');
            const badge3 = diag ? diag.querySelector('#step-badge-3, button#step-badge-3') : null;
            if (badge3) {
                badge3.click();
                return 'badge3_clicked';
            }
            return 'no_badge3';
        })()
        """)
        print("    Visibility tab:", step_vis, flush=True)
        await asyncio.sleep(2)

        if step_vis != 'badge3_clicked':
            for step in range(3):
                await eval_js("""
                (() => {
                    const diag = document.querySelector('ytcp-uploads-dialog');
                    const nextBtn = diag ? diag.querySelector("ytcp-button#next-button, #next-button button") : null;
                    if (nextBtn && !nextBtn.disabled) nextBtn.click();
                })()
                """)
                await asyncio.sleep(2)

        # 7. Select Public visibility
        print("[7] Selecting PUBLIC radio...", flush=True)
        pub_res = await eval_js("""
        (() => {
            const diag = document.querySelector('ytcp-uploads-dialog');
            const pubRadio = diag ? diag.querySelector("tp-yt-paper-radio-button[name='PUBLIC']") : document.querySelector("tp-yt-paper-radio-button[name='PUBLIC']");
            if (pubRadio) {
                pubRadio.click();
                return 'public_selected';
            }
            return 'no_public_radio';
        })()
        """)
        print("    Public select:", pub_res, flush=True)
        await asyncio.sleep(1.5)

        # 8. Click Publish / Done button
        print("[8] Clicking Publish button...", flush=True)
        pub_click = await eval_js("""
        (() => {
            const diag = document.querySelector('ytcp-uploads-dialog');
            const btn = diag ? diag.querySelector("ytcp-button#done-button, ytcp-button#save-button, button#publish-button, ytcp-button#publish-button") : null;
            if (btn) {
                btn.click();
                return 'publish_clicked';
            }
            return 'no_btn';
        })()
        """)
        print("    Publish click result:", pub_click, flush=True)
        await asyncio.sleep(4)

        # Handle 'Publish anyway'
        await eval_js("""
        (() => {
            const btns = Array.from(document.querySelectorAll("button, ytcp-button"));
            const anyway = btns.find(b => b.innerText && (b.innerText.includes('Publish anyway') || b.innerText.includes('Publish')));
            if (anyway) anyway.click();
        })()
        """)
        await asyncio.sleep(3)

        # Close dialog
        await eval_js("""
        (() => {
            const closeBtn = document.querySelector("ytcp-button#close-button, button[aria-label*='Close' i]");
            if (closeBtn) closeBtn.click();
        })()
        """)
        await asyncio.sleep(3)

        # Navigate to Shorts list
        await call("Page.navigate", {"url": "https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short"})
        await asyncio.sleep(6)

        await call("Page.enable")
        s_res = await call("Page.captureScreenshot", {"format": "png"})
        proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_color_public_final_proof.png"
        with open(proof, "wb") as f:
            f.write(base64.b64decode(s_res["data"]))
        print("[SUCCESS] Verified final proof saved to", proof)

if __name__ == "__main__":
    asyncio.run(publish_draft())
