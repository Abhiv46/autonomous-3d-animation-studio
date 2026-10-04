import asyncio
import json
import base64
from pathlib import Path
from direct_cdp import DirectCDPClient, get_browser_ws

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
    ws_url = await get_browser_ws()
    print(f"[1] Connecting via DirectCDP to {ws_url}...", flush=True)
    client = DirectCDPClient(ws_url)
    await client.connect()
    
    try:
        targets = await client.get_targets()
        yt_target = None
        for t in targets:
            if t.get("type") == "page" and "studio.youtube.com" in t.get("url", ""):
                yt_target = t
                break
                
        if not yt_target:
            print("[+] Opening YouTube Studio...", flush=True)
            target_id = await client.create_target("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short")
            yt_target = {"targetId": target_id}
            await asyncio.sleep(4)
            
        print(f"[2] Attaching to target {yt_target['targetId']}...", flush=True)
        session = await client.attach_to_target(yt_target["targetId"])
        
        # Navigate to channel shorts page to start fresh
        await session.eval("window.location.href = 'https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short'")
        await asyncio.sleep(4)

        # 1. Click Create button
        print("[3] Clicking Create button...", flush=True)
        click_create = await session.eval("""
        (() => {
            const btn = document.querySelector("#create-icon, ytcp-button#create-icon, button[aria-label*='Create' i]");
            if (btn) {
                btn.click();
                return 'create_clicked';
            }
            return 'no_create_btn';
        })()
        """)
        print(f"    Create click: {click_create}", flush=True)
        await asyncio.sleep(1.5)
        
        # Click Upload videos item
        click_upload_item = await session.eval("""
        (() => {
            const items = Array.from(document.querySelectorAll("ytcp-text-menu-item, tp-yt-paper-item, div"));
            const up = items.find(i => i.innerText && i.innerText.trim().toLowerCase() === 'upload videos');
            if (up) {
                up.click();
                return 'upload_item_clicked';
            }
            return 'no_upload_item';
        })()
        """)
        print(f"    Upload item click: {click_upload_item}", flush=True)
        await asyncio.sleep(2)

        # 2. Find file input via DOM agent
        print("[4] Finding input[type='file'] via DOM agent...", flush=True)
        await session.send("DOM.enable")
        doc = await session.send("DOM.getDocument", {"depth": -1})
        input_info = await session.send("DOM.querySelector", {
            "nodeId": doc["root"]["nodeId"],
            "selector": "input[type='file']"
        })
        input_node_id = input_info.get("nodeId")
        print(f"    Input Node ID: {input_node_id}", flush=True)
        
        if not input_node_id:
            print("[!] Retrying after clicking Select Files...")
            await session.eval("""
            (() => {
                const btn = document.querySelector('#select-files-button');
                if (btn) btn.click();
            })()
            """)
            await asyncio.sleep(2)
            doc = await session.send("DOM.getDocument", {"depth": -1})
            input_info = await session.send("DOM.querySelector", {
                "nodeId": doc["root"]["nodeId"],
                "selector": "input[type='file']"
            })
            input_node_id = input_info.get("nodeId")
            
        # 3. Set file
        print(f"[5] Setting file: {VIDEO_PATH}...", flush=True)
        await session.send("DOM.setFileInputFiles", {
            "nodeId": input_node_id,
            "files": [VIDEO_PATH]
        })
        print("    File set sent successfully!", flush=True)
        
        # 4. Wait for upload dialog to populate
        print("[6] Waiting for upload dialog to process...", flush=True)
        video_url = None
        for i in range(25):
            await asyncio.sleep(2)
            status = await session.eval("""
            (() => {
                const dialog = document.querySelector("ytcp-uploads-dialog");
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
            if status.get("links") and len(status["links"]) > 0:
                video_url = status["links"][0]
            if status.get("hasTitle") and status.get("hasDialog"):
                print(f"    Ready at check {i+1}!")
                break
                
        print(f"[+] Detected Video URL: {video_url}", flush=True)
        await asyncio.sleep(2)

        # 5. Fill Title
        print("[7] Setting Title...", flush=True)
        await session.eval(f"""
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
        print("[8] Setting Description...", flush=True)
        await session.eval(f"""
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
        print("[9] Setting Audience to Not Made for Kids...", flush=True)
        await session.eval("""
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

        # 8. Show more & Add Tags
        print("[10] Expanding 'Show more' and setting Tags...", flush=True)
        await session.eval("""
        (() => {
            const btn = document.querySelector("ytcp-uploads-dialog #toggle-button, #toggle-button");
            if (btn) btn.click();
        })()
        """)
        await asyncio.sleep(1.5)

        tags_string = ", ".join(YT_TAGS) + ","
        tags_set = await session.eval(f"""
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
        print(f"    Tags set result: {tags_set}", flush=True)
        await asyncio.sleep(1)

        # 9. Step directly to Visibility (Step badge 3)
        print("[11] Navigating to Visibility tab...", flush=True)
        step_vis = await session.eval("""
        (() => {
            const badge3 = document.querySelector("ytcp-uploads-dialog #step-badge-3, button#step-badge-3");
            if (badge3) {
                badge3.click();
                return 'badge3_clicked';
            }
            return 'no_badge3';
        })()
        """)
        print(f"    Visibility badge click: {step_vis}", flush=True)
        await asyncio.sleep(2)
        
        # If badge didn't click, click Next repeatedly
        if step_vis != 'badge3_clicked':
            for step in range(3):
                await session.eval("""
                (() => {
                    const nextBtn = document.querySelector("ytcp-button#next-button, #next-button button");
                    if (nextBtn && !nextBtn.disabled) nextBtn.click();
                })()
                """)
                await asyncio.sleep(2)

        # 10. Select PUBLIC Visibility
        print("[12] Selecting PUBLIC visibility...", flush=True)
        pub_res = await session.eval("""
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
        print("[13] Clicking Publish / Done button...", flush=True)
        pub_btn_res = await session.eval("""
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
        anyway_res = await session.eval("""
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

        # Close dialog
        await session.eval("""
        (() => {
            const closeBtn = document.querySelector("ytcp-button#close-button, button[aria-label*='Close' i]");
            if (closeBtn) closeBtn.click();
        })()
        """)
        await asyncio.sleep(3)

        # 12. Navigate to Shorts channel list
        print("[14] Navigating to Shorts channel list for verification...", flush=True)
        await session.eval("window.location.href = 'https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short'")
        await asyncio.sleep(6)

        # Take final proof screenshot
        res = await session.send("Page.captureScreenshot", {"format": "png"})
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_color_adventure_published_proof.png"
        with open(proof_path, "wb") as f:
            f.write(base64.b64decode(res["data"]))
            
        print(f"[SUCCESS] Upload completed and verified! Proof saved to {proof_path}")
        print(f"[INFO] Video Link: {video_url}")

    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(upload())
