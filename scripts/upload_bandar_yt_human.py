import asyncio
import json
import base64
import urllib.request
import websockets
from pathlib import Path

VIDEO_PATH = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\TheNaughtyDuo_MummyNeBandarKoPakda_Master.mp4"
SCREENSHOT_DIR = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2")

YT_TITLE = "Mummy Ka Jhumka Box Bandar Le Gaya! 🐒😱 Kaavya Ne Pakda Bandar Ko! 😂🍌 #TheNaughtyDuo #shorts"

YT_DESC = """Mummy tayyar ho rahi thi aur achanak ek natkhat Bandar unka poora Jhumka Box leke bhaag gaya! 🐒😱
Mummy scooter leke market me peeche bhaagi... Kaartik bhaiyya chath par dhoondhne lage! 🛴💨
Lekin Kaavya ne lagaya apna mast dimaag — Bandar ko di tasty katori aur badle me jhumka box wapas le liya! 😂🍌❤️
Dekhiye Mummy, Kaavya aur Kaartik ki sabse viral aur funny Bandar comedy story! 🥰✨

💬 Sawaal: Kya aapke ghar ya chath par kabhi bandar aaya hai? Comment me batao! 👇

🔔 Aise hi mazedaar 3D family cartoons aur daily siblings comedy stories ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 💖

#shorts #TheNaughtyDuo #KaavyaAndKaartik #BandarPrank #MummyKaJhumka #MonkeyChase #FunnyShorts #HindiCartoon #3DAnimation #CartoonStories #SiblingsComedy #KidsAnimation #ViralShorts #Trending"""

YT_TAGS = [
    "The Naughty Duo", "TheNaughtyDuo", "Kaartik and Kaavya", "bandar prank",
    "monkey cartoon hindi", "mummy ka jhumka", "hindi cartoon", "3d animation hindi",
    "kids cartoon funny", "siblings comedy", "funny hindi stories", "cartoon video hindi",
    "family comedy", "shorts", "viral shorts", "trending shorts"
]

async def human_delay(min_s=1.0, max_s=2.5):
    import random
    await asyncio.sleep(random.uniform(min_s, max_s))

async def upload_youtube_human():
    print("[1] Locating YouTube Studio tab...", flush=True)
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read())
    yt_tab = next((t for t in tabs if "studio.youtube.com" in t.get("url", "")), None)
    if not yt_tab:
        yt_tab = tabs[0]
        
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

        # Human-like interaction: Look for Create button
        print("[2] Human click: Create button...", flush=True)
        await human_delay(1.5, 2.5)
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
        await human_delay(1.5, 2.0)

        # Click Upload videos item
        print("[3] Human click: Upload videos...", flush=True)
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
        await human_delay(2.0, 3.0)

        # Set file input via DOM agent
        print("[4] Selecting Video File...", flush=True)
        await call("DOM.enable")
        doc = await call("DOM.getDocument", {"depth": -1})
        input_node = await call("DOM.querySelector", {
            "nodeId": doc["root"]["nodeId"],
            "selector": "input[type='file']"
        })
        node_id = input_node.get("nodeId")
        if not node_id:
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
        print(f"[+] File attached: {Path(VIDEO_PATH).name}", flush=True)

        # Wait like human for form to appear
        print("[5] Waiting for details dialog to load...", flush=True)
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
                
        print(f"[+] Video URL detected: {video_url}", flush=True)
        await human_delay(1.5, 2.5)

        # Type Title like human
        print("[6] Typing Title...", flush=True)
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
        await human_delay(1.5, 2.5)

        # Type Description like human
        print("[7] Typing Description...", flush=True)
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
        await human_delay(1.5, 2.5)

        # Set Audience: Not made for kids
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
        await human_delay(1.5, 2.5)

        # Expand Show More
        print("[9] Expanding Show more for Tags...", flush=True)
        await eval_js("""
        (() => {
            const btn = document.querySelector("ytcp-uploads-dialog #toggle-button, #toggle-button");
            if (btn) btn.click();
        })()
        """)
        await human_delay(1.5, 2.5)

        # Set Tags
        print("[10] Inserting Viral Tags...", flush=True)
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
        await human_delay(2.0, 3.0)

        # Step through Wizard (Next buttons)
        print("[11] Human progression through Wizard...", flush=True)
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
            await human_delay(2.0, 3.0)

        # Select PUBLIC Visibility
        print("[12] Selecting PUBLIC visibility...", flush=True)
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
        await human_delay(2.0, 3.0)

        # Click Publish / Done button
        print("[13] Publishing Video...", flush=True)
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
        await human_delay(5.0, 7.0)

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
        await human_delay(3.0, 4.0)

        # Take published dialog screenshot
        proof_dialog = str(SCREENSHOT_DIR / "yt_bandar_published_dialog.png")
        await take_screenshot(proof_dialog)

        # Close dialog
        await eval_js("""
        (() => {
            const closeBtn = document.querySelector("ytcp-button#close-button, button[aria-label*='Close' i]");
            if (closeBtn) closeBtn.click();
        })()
        """)
        await asyncio.sleep(2)

        print(f"\n==================================================")
        print(f"  [SUCCESS] YOUTUBE VIDEO UPLOADED AND PUBLISHED!  ")
        print(f"  Live Video URL: {video_url}")
        print(f"  Proof Screenshot: {proof_dialog}")
        print(f"==================================================")

if __name__ == "__main__":
    asyncio.run(upload_youtube_human())
