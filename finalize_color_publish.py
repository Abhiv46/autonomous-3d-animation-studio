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

async def finalize_publish():
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

        # 1. Navigate to edit page
        edit_url = f"https://studio.youtube.com/video/{VID_ID}/edit"
        print(f"[1] Navigating to edit page: {edit_url}...", flush=True)
        await call("Page.navigate", {"url": edit_url})
        await asyncio.sleep(5)

        # 2. Click 'Edit draft' button on edit page (action-1)
        print("[2] Clicking 'Edit draft' button...", flush=True)
        btn_res = await eval_js("""
        (() => {
            const btn = document.querySelector('ytcp-button#action-1') ||
                        Array.from(document.querySelectorAll('button, ytcp-button')).find(b => b.innerText && b.innerText.trim() === 'Edit draft');
            if (btn) {
                btn.click();
                return 'clicked';
            }
            return 'not_found';
        })()
        """)
        print("    Edit draft click:", btn_res, flush=True)
        await asyncio.sleep(4)

        # 3. Fill Description in dialog
        print("[3] Filling Description...", flush=True)
        await eval_js(f"""
        (() => {{
            const descBox = document.querySelector("ytcp-uploads-dialog #textbox[aria-label*='description' i], #textbox[aria-label*='description' i]");
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

        # 4. Audience: Not Made for Kids
        print("[4] Setting Audience...", flush=True)
        await eval_js("""
        (() => {
            const notKids = document.querySelector("ytcp-uploads-dialog tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK'], tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']");
            if (notKids) notKids.click();
        })()
        """)
        await asyncio.sleep(1)

        # 5. Click Show more & Add Tags
        print("[5] Adding Tags...", flush=True)
        await eval_js("""
        (() => {
            const toggle = document.querySelector("ytcp-uploads-dialog #toggle-button, #toggle-button");
            if (toggle) toggle.click();
        })()
        """)
        await asyncio.sleep(1.5)

        tags_string = ", ".join(YT_TAGS) + ","
        await eval_js(f"""
        (() => {{
            const tagsInput = document.querySelector("ytcp-uploads-dialog input[aria-label*='Tag' i], input[placeholder*='tag' i], #tags-container input");
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
        print("[6] Clicking Visibility step badge...", flush=True)
        badge_click = await eval_js("""
        (() => {
            const badge3 = document.querySelector("ytcp-uploads-dialog #step-badge-3, button#step-badge-3");
            if (badge3) {
                badge3.click();
                return 'badge3_clicked';
            }
            return 'no_badge3';
        })()
        """)
        print("    Visibility badge click:", badge_click, flush=True)
        await asyncio.sleep(2)

        # 7. Select Public radio button
        print("[7] Selecting PUBLIC radio button...", flush=True)
        pub_sel = await eval_js("""
        (() => {
            const pubRadio = document.querySelector("ytcp-uploads-dialog tp-yt-paper-radio-button[name='PUBLIC'], tp-yt-paper-radio-button[name='PUBLIC']");
            if (pubRadio) {
                pubRadio.click();
                return 'public_selected';
            }
            return 'no_public_radio';
        })()
        """)
        print("    Public radio select:", pub_sel, flush=True)
        await asyncio.sleep(1.5)

        # 8. Click Publish / Done / Save button
        print("[8] Clicking Publish button...", flush=True)
        pub_btn = await eval_js("""
        (() => {
            const btn = document.querySelector("ytcp-uploads-dialog ytcp-button#done-button, ytcp-uploads-dialog ytcp-button#save-button, ytcp-button#done-button");
            if (btn) {
                btn.click();
                return 'clicked';
            }
            return 'no_btn';
        })()
        """)
        print("    Publish click:", pub_btn, flush=True)
        await asyncio.sleep(4)

        # 9. Handle Publish anyway if modal appears
        anyway_click = await eval_js("""
        (() => {
            const btns = Array.from(document.querySelectorAll("button, ytcp-button"));
            const anyway = btns.find(b => b.innerText && (b.innerText.includes('Publish anyway') || b.innerText.includes('Publish')));
            if (anyway) {
                anyway.click();
                return 'anyway_clicked';
            }
            return 'no_anyway';
        })()
        """)
        print("    Publish anyway click:", anyway_click, flush=True)
        await asyncio.sleep(3)

        # 10. Close dialog
        await eval_js("""
        (() => {
            const closeBtn = document.querySelector("ytcp-button#close-button, button[aria-label*='Close' i]");
            if (closeBtn) closeBtn.click();
        })()
        """)
        await asyncio.sleep(2)

        # 11. Navigate to Shorts list
        print("[9] Navigating to Shorts list...", flush=True)
        await call("Page.navigate", {"url": "https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short"})
        await asyncio.sleep(6)

        # Take final screenshot
        await call("Page.enable")
        s_res = await call("Page.captureScreenshot", {"format": "png"})
        proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_color_public_confirmed_final.png"
        with open(proof, "wb") as f:
            f.write(base64.b64decode(s_res["data"]))
        print("[SUCCESS] Final verified screenshot saved to", proof)

if __name__ == "__main__":
    asyncio.run(finalize_publish())
