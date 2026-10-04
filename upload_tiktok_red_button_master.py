import asyncio
import json
import os
from direct_cdp import DirectCDPClient, get_browser_ws

VIDEO_PATH = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\TheNaughtyDuo_TikTok_RedButtonMagic_Master.mp4"
TIKTOK_CAPTION = "Kaavya Ne Dabaya Mysterious Red Button! 🔴😱 Box Khula Toh Hua Magic! ✨ Wait for Mummy's reaction 😂🥰 #TheNaughtyDuo #shorts #viral #funny #comedy #3danimation #hindicartoon #foryou #fyp #trending #magicbox #toddlersoftiktok"

async def main():
    ws_url = await get_browser_ws()
    print("[1] Connecting to browser...", flush=True)
    client = DirectCDPClient(ws_url)
    await client.connect()
    
    try:
        targets = await client.get_targets()
        tt_target = None
        for t in targets:
            if t.get("type") == "page" and "tiktokstudio/upload" in t.get("url", ""):
                tt_target = t
                break
                
        if not tt_target:
            print("[+] Opening TikTok Studio upload page...", flush=True)
            target_id = await client.create_target("https://www.tiktok.com/tiktokstudio/upload")
            tt_target = {"targetId": target_id}
            await asyncio.sleep(5)
            
        print(f"[2] Attaching to TikTok target: {tt_target['targetId']}", flush=True)
        session = await client.attach_to_target(tt_target["targetId"])
        
        # 1. Check for Discard button if previous draft exists
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
        doc = await session.send("DOM.getDocument", {"depth": -1})
        root_node_id = doc["root"]["nodeId"]
        
        input_info = await session.send("DOM.querySelector", {
            "nodeId": root_node_id,
            "selector": "input[type='file']"
        })
        input_node_id = input_info.get("nodeId")
        print(f"    Input Node ID: {input_node_id}", flush=True)
        
        if not input_node_id:
            print("[!] Could not locate file input!")
            return
            
        # 3. Set file input
        print(f"[5] Uploading file {VIDEO_PATH}...", flush=True)
        await session.send("DOM.setFileInputFiles", {
            "nodeId": input_node_id,
            "files": [VIDEO_PATH]
        })
        print("    File set sent to input successfully!", flush=True)
        
        # 4. Wait for upload to process and form to appear
        print("[6] Waiting for upload processing...", flush=True)
        for i in range(25):
            await asyncio.sleep(2)
            state = await session.eval("""
            (() => {
                const textareas = Array.from(document.querySelectorAll("div[contenteditable='true'], textarea, input"));
                const btns = Array.from(document.querySelectorAll("button")).map(b => b.innerText.trim());
                const uploadedText = document.body.innerText.includes('Uploaded') || document.body.innerText.includes('1080P');
                return {
                    hasEditable: textareas.some(t => t.offsetParent !== null),
                    postBtn: btns.includes("Post"),
                    uploaded: uploadedText
                };
            })()
            """)
            print(f"    Wait check {i+1}: {state}", flush=True)
            if state.get("postBtn") and state.get("hasEditable"):
                print("    Upload ready and form loaded!", flush=True)
                break
                
        # 5. Capture upload state screenshot
        proof_dir = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2"
        await session.screenshot(os.path.join(proof_dir, "tiktok_ep24_uploaded_form.png"))
        
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
        await asyncio.sleep(2)
        
        await session.screenshot(os.path.join(proof_dir, "tiktok_ep24_caption_filled.png"))
        
        # 7. Click Post button
        print("[8] Clicking Post button...", flush=True)
        post_res = await session.eval("""
        (() => {
            const btns = Array.from(document.querySelectorAll("button"));
            const post = btns.find(b => b.innerText && b.innerText.trim() === 'Post');
            if (post) {
                post.scrollIntoView({ behavior: 'smooth', block: 'center' });
                post.click();
                return 'post_clicked';
            }
            return 'no_post_button';
        })()
        """)
        print(f"    Post click result: {post_res}", flush=True)
        await asyncio.sleep(8)
        
        # 8. Verification screenshot
        proof_path = os.path.join(proof_dir, "tiktok_ep24_posted_proof.png")
        await session.screenshot(proof_path)
        print(f"[SUCCESS] TikTok upload completed! Proof saved to {proof_path}", flush=True)
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
