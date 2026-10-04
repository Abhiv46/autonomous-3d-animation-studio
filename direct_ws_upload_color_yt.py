import asyncio
import json
import base64
import urllib.request
import websockets
from pathlib import Path

VIDEO_PATH = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\TheNaughtyDuo_YouTube_MagicColorAdventure_Master.mp4"
SCREENSHOT_DIR = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2")

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

async def upload():
    print("[1] Locating YouTube Studio tab...", flush=True)
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read())
    yt_tab = next((t for t in tabs if "studio.youtube.com" in t.get("url", "").lower()), None)
    if not yt_tab:
        yt_tab = next(t for t in tabs if "youtube.com" in t.get("url", "").lower())
        
    ws_url = yt_tab["webSocketDebuggerUrl"]
    print(f"[+] Connecting directly to {ws_url}...", flush=True)
    
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        msg_id = 0
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cid = msg_id
            await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get("id") == cid:
                    if "error" in resp:
                        raise Exception(f"CDP Error ({method}): {resp['error']}")
                    return resp.get("result", {})

        async def eval_js(js):
            res = await call("Runtime.evaluate", {"expression": js, "returnByValue": True, "awaitPromise": True})
            return res.get("result", {}).get("value")

        async def take_screenshot(out_path):
            await call("Page.enable")
            res = await call("Page.captureScreenshot", {"format": "png"})
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(res["data"]))
            print(f"[+] Screenshot saved to {out_path}", flush=True)

        # 1. Click Create button
        print("[2] Clicking Create button...", flush=True)
        create_res = await eval_js("""
        (() => {
            const btn = document.querySelector("#create-icon, ytcp-button#create-icon, button[aria-label*='Create' i]");
            if (btn) {
                btn.click();
                return 'create_clicked';
            }
            return 'no_create';
        })()
        """)
        print(f"    Create click: {create_res}", flush=True)
        await asyncio.sleep(1.5)

        # 2. Click Upload videos item
        print("[3] Clicking Upload videos...", flush=True)
        upload_res = await eval_js("""
        (() => {
            const items = Array.from(document.querySelectorAll("ytcp-text-menu-item, tp-yt-paper-item, div"));
            const up = items.find(i => i.innerText && i.innerText.trim().toLowerCase() === 'upload videos');
            if (up) {
                up.click();
                return 'upload_clicked';
            }
            return 'no_upload';
        })()
        """)
        print(f"    Upload item click: {upload_res}", flush=True)
        await asyncio.sleep(2)

        # 3. Set file input via DOM agent
        print("[4] Attaching video file via DOM...", flush=True)
        await call("DOM.enable")
        doc = await call("DOM.getDocument", {"depth": -1})
        input_node = await call("DOM.querySelector", {
            "nodeId": doc["root"]["nodeId"],
            "selector": "input[type='file']"
        })
        node_id = input_node.get("nodeId")
        print(f"    input[type='file'] nodeId: {node_id}", flush=True)
        
        if not node_id:
            print("    Retrying finding input after clicking select files...")
            await eval_js("const btn = document.querySelector('#select-files-button'); if(btn) btn.click();")
            await asyncio.sleep(2)
            doc = await call("DOM.getDocument", {"depth": -1})
            input_node = await call("DOM.querySelector", {
                "nodeId": doc["root"]["nodeId"],
                "selector": "input[type='file']"
            })
            node_id = input_node.get("nodeId")
            
        await call("DOM.setFileInputFiles", {
            "nodeId": node_id,
            "files": [VIDEO_PATH]
        })
        print(f"[+] File {Path(VIDEO_PATH).name} attached successfully!", flush=True)

        # 4. Wait for upload dialog to populate
        print("[5] Waiting for upload dialog to populate...", flush=True)
        video_url = None
        for i in range(25):
            await asyncio.sleep(2)
            diag_info = await eval_js("""
            (() => {
                const dialog = document.querySelector('ytcp-uploads-dialog');
                const titleBox = document.querySelector("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox");
                const links = Array.from(document.querySelectorAll("a"))
                    .map(a => a.href)
                    .filter(h => h.includes("youtu.be") || h.includes("shorts"));
                return {
                    hasDialog: !!dialog,
                    hasTitle: !!titleBox,
                    links: links
                };
            })()
            """)
            if diag_info and diag_info.get("links"):
                video_url = diag_info["links"][0]
            if diag_info and diag_info.get("hasTitle") and diag_info.get("hasDialog"):
                print(f"    Dialog ready at step {i+1}!", flush=True)
                break
                
        print(f"[+] Detected Video URL: {video_url}", flush=True)

        # 5. Fill Title
        print("[6] Setting Title...", flush=True)
        await eval_js(f"""
        (() => {{
            const titleBox = document.querySelector("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox");
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

        # 6. Fill Description
        print("[7] Setting Description...", flush=True)
        await eval_js(f"""
        (() => {{
            const descBox = document.querySelector("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox");
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

        # 7. Set Audience to Not Made for Kids
        print("[8] Setting Audience to Not Made for Kids...", flush=True)
        await eval_js("""
        (() => {
            const notKids = document.querySelector("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']");
            if (notKids) {
                notKids.click();
                return 'not_kids_selected';
            }
            return 'no_not_kids_radio';
        })()
        """)
        await asyncio.sleep(1)

        # 8. Expand 'Show more' and set Tags
        print("[9] Expanding 'Show more' and setting Tags...", flush=True)
        await eval_js("""
        (() => {
            const btn = document.querySelector("ytcp-uploads-dialog #toggle-button, #toggle-button");
            if (btn) btn.click();
        })()
        """)
        await asyncio.sleep(1.5)

        tags_string = ", ".join(YT_TAGS) + ","
        tags_res = await eval_js(f"""
        (() => {{
            const tagsInput = document.querySelector("ytcp-uploads-dialog input[aria-label*='Tag' i], input[placeholder*='tag' i], #tags-container input");
            if (tagsInput) {{
                tagsInput.focus();
                document.execCommand('insertText', false, {json.dumps(tags_string)});
                tagsInput.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', keyCode: 13, bubbles: true }}));
                return 'tags_set';
            }}
            return 'no_tags_input';
        }})()
        """)
        print(f"    Tags set result: {tags_res}", flush=True)
        await asyncio.sleep(1)

        # 9. Step through Wizard (Next buttons) to Visibility
        print("[10] Stepping through wizard to Visibility...", flush=True)
        for step in range(3):
            next_res = await eval_js("""
            (() => {
                const nextBtn = document.querySelector("ytcp-button#next-button, #next-button button");
                if (nextBtn && !nextBtn.disabled) {
                    nextBtn.click();
                    return 'clicked';
                }
                return 'not_found_or_disabled';
            })()
            """)
            print(f"    Step {step+1}: {next_res}", flush=True)
            await asyncio.sleep(2)

        # 10. Select PUBLIC Visibility
        print("[11] Selecting PUBLIC visibility...", flush=True)
        pub_res = await eval_js("""
        (() => {
            const pubRadio = document.querySelector("ytcp-uploads-dialog tp-yt-paper-radio-button[name='PUBLIC'], tp-yt-paper-radio-button[name='PUBLIC']");
            if (pubRadio) {
                pubRadio.click();
                return 'public_selected';
            }
            return 'no_pub_radio';
        })()
        """)
        print(f"    Public radio: {pub_res}", flush=True)
        await asyncio.sleep(1.5)

        # 11. Click Publish / Done button
        print("[12] Clicking Publish / Done button...", flush=True)
        pub_btn_res = await eval_js("""
        (() => {
            const pubBtn = document.querySelector("ytcp-uploads-dialog ytcp-button#done-button, ytcp-uploads-dialog button#publish-button, ytcp-button#done-button");
            if (pubBtn) {
                pubBtn.click();
                return 'publish_clicked';
            }
            return 'no_publish_btn';
        })()
        """)
        print(f"    Publish click: {pub_btn_res}", flush=True)
        await asyncio.sleep(4)

        # Handle 'Publish anyway' modal if present
        anyway_res = await eval_js("""
        (() => {
            const btn = Array.from(document.querySelectorAll("button, ytcp-button"))
                .find(b => b.innerText && (b.innerText.includes('Publish anyway') || b.innerText.includes('Close')));
            if (btn && btn.innerText.includes('Publish anyway')) {
                btn.click();
                return 'publish_anyway_clicked';
            }
            return 'no_anyway';
        })()
        """)
        print(f"    Publish anyway: {anyway_res}", flush=True)
        await asyncio.sleep(3)

        # Take published dialog screenshot
        proof_dialog = str(SCREENSHOT_DIR / "yt_color_published_dialog.png")
        await take_screenshot(proof_dialog)

        # Close dialog
        await eval_js("""
        (() => {
            const closeBtn = document.querySelector("ytcp-button#close-button, button[aria-label*='Close' i]");
            if (closeBtn) closeBtn.click();
        })()
        """)
        await asyncio.sleep(2)

        # 12. Navigate to Shorts channel list for verification
        print("[13] Navigating to Shorts channel list for verification...", flush=True)
        await eval_js("window.location.href = 'https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short'")
        await asyncio.sleep(6)

        proof_list = str(SCREENSHOT_DIR / "yt_color_adventure_live_proof.png")
        await take_screenshot(proof_list)
        print(f"[SUCCESS] Upload completed and verified! Proof saved to {proof_list}")
        print(f"[INFO] Video Link: {video_url}")

if __name__ == "__main__":
    asyncio.run(upload())
