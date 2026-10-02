import asyncio
import json
import os
from direct_cdp import DirectCDPClient, get_browser_ws

VIDEO_PATH = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\processed_episodes\TheNaughtyDuo_EP22_OriginalAudio_Master.mp4"
TIKTOK_CAPTION = "Magical Glowing Gulab Jamun Chori! 🍯😱 Kaartik ne pakad liya Kaavya ko! Wait for the sweet ending 🥰❤️ #TheNaughtyDuo #shorts #viral #funny #comedy #3danimation #hindicartoon #foryou #fyp #trending #gulabjamun"

async def main():
    ws_url = await get_browser_ws()
    print("[1] Connecting to browser...", flush=True)
    client = DirectCDPClient(ws_url)
    await client.connect()
    
    try:
        targets = await client.get_targets()
        tt_target = None
        for t in targets:
            if t.get("type") == "page" and "tiktok.com" in t.get("url", ""):
                tt_target = t
                break
                
        # If no TikTok target exists, create one
        if not tt_target:
            print("[+] Opening new TikTok Studio upload page...", flush=True)
            new_target = await client.create_target("https://www.tiktok.com/tiktokstudio/upload")
            tt_target = {"targetId": new_target["targetId"]}
            await asyncio.sleep(5)
            
        print(f"[2] Attaching to TikTok target: {tt_target['targetId']}", flush=True)
        session = await client.attach_to_target(tt_target["targetId"])
        
        # 1. Click Discard if "Discard" button is visible
        print("[3] Checking for Discard button...", flush=True)
        discard_res = await session.eval("""
        (() => {
            const btns = Array.from(document.querySelectorAll("button"));
            const discard = btns.find(b => b.innerText && b.innerText.trim() === 'Discard');
            if (discard) {
                discard.click();
                return 'discard_clicked';
            }
            return 'no_discard';
        })()
        """)
        print(f"    Discard result: {discard_res}", flush=True)
        await asyncio.sleep(2)
        
        # 2. Get DOM document and input[type='file'] nodeId
        print("[4] Finding file input nodeId via CDP DOM...", flush=True)
        await session.send("DOM.enable")
        doc = await session.send("DOM.getDocument")
        root_node_id = doc["root"]["nodeId"]
        
        input_info = await session.send("DOM.querySelector", {
            "nodeId": root_node_id,
            "selector": "input[type='file']"
        })
        input_node_id = input_info.get("nodeId")
        print(f"    Input Node ID: {input_node_id}", flush=True)
        
        if not input_node_id:
            # Maybe inside an iframe? Let's check iframes
            print("[!] File input not found at root, checking iframes...", flush=True)
            doc_deep = await session.send("DOM.getDocument", {"depth": -1})
            # Find file input anywhere
            input_info = await session.send("DOM.querySelector", {
                "nodeId": doc_deep["root"]["nodeId"],
                "selector": "input[type='file']"
            })
            input_node_id = input_info.get("nodeId")
            print(f"    Deep Input Node ID: {input_node_id}", flush=True)
            
        if not input_node_id:
            print("[!] Could not locate file input!")
            return
            
        # 3. Set file input
        print(f"[5] Uploading file {VIDEO_PATH}...", flush=True)
        await session.send("DOM.setFileInputFiles", {
            "nodeId": input_node_id,
            "files": [VIDEO_PATH]
        })
        print("    File set sent to input!", flush=True)
        
        # 4. Wait for upload to process and form to appear
        print("[6] Waiting for upload processing...", flush=True)
        for i in range(15):
            await asyncio.sleep(2)
            state = await session.eval("""
            (() => {
                const textareas = Array.from(document.querySelectorAll("div[contenteditable='true'], textarea, input"));
                const btns = Array.from(document.querySelectorAll("button")).map(b => b.innerText.trim());
                const progress = document.querySelector(".upload-progress, [class*='progress']");
                return {
                    hasEditable: textareas.some(t => t.offsetParent !== null),
                    postBtn: btns.includes("Post"),
                    progress: progress ? progress.innerText : null
                };
            })()
            """)
            print(f"    Wait check {i+1}: {state}", flush=True)
            if state.get("postBtn") or state.get("hasEditable"):
                break
                
        # 5. Capture upload state screenshot
        await session.screenshot(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\tiktok_ep22_file_set.png")
        
        # 6. Fill Caption
        print("[7] Filling Caption and Hashtags...", flush=True)
        fill_res = await session.eval(f"""
        (() => {{
            const editor = document.querySelector("div[contenteditable='true']");
            if (editor) {{
                editor.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, {json.dumps(TIKTOK_CAPTION)});
                editor.dispatchEvent(new Event('input', {{ bubbles: true }}));
                return 'caption_set';
            }}
            return 'no_editor_found';
        }})()
        """)
        print(f"    Fill result: {fill_res}", flush=True)
        await asyncio.sleep(3)
        
        # 7. Click Post button
        print("[8] Clicking Post button...", flush=True)
        post_res = await session.eval("""
        (() => {
            const btns = Array.from(document.querySelectorAll("button"));
            const post = btns.find(b => b.innerText && b.innerText.trim() === 'Post');
            if (post) {
                post.click();
                return 'post_clicked';
            }
            return 'no_post_button';
        })()
        """)
        print(f"    Post click result: {post_res}", flush=True)
        await asyncio.sleep(6)
        
        # 8. Verification screenshot
        screenshot_path = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\tiktok_ep22_posted.png"
        await session.screenshot(screenshot_path)
        print(f"[SUCCESS] TikTok upload process executed! Proof saved to {screenshot_path}", flush=True)
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
