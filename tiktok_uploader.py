import asyncio
import json
import os
from direct_cdp import DirectCDPClient, get_browser_ws

VIDEO_PATH = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\processed_episodes\TheNaughtyDuo_EP21_MummyKiHighHeels_OriginalAudio_Master.mp4"
TIKTOK_CAPTION = "Kaavya ne pehni Mummy ki high heels! 😂👠 Sassy fashion model Kaavya ko pakad liya! Wait for cute reaction 🥰❤️ #TheNaughtyDuo #shorts #viral #funny #comedy #3danimation #hindicartoon #foryou #fyp #trending"

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
                
        if not tt_target:
            print("[!] TikTok target not found!")
            return
            
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
            print("[!] File input element not found in DOM!")
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
        for i in range(12):
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
        await session.screenshot(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\tiktok_after_file_set.png")
        
        # 6. Fill Caption
        print("[7] Filling Caption and Hashtags...", flush=True)
        fill_res = await session.eval("""
        (() => {
            const editor = document.querySelector("div[contenteditable='true']");
            if (editor) {
                editor.focus();
                // Set text directly
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, """ + json.dumps(TIKTOK_CAPTION) + """);
                return 'caption_set_contenteditable';
            }
            const textarea = document.querySelector("textarea[placeholder*='caption' i], textarea");
            if (textarea) {
                textarea.value = """ + json.dumps(TIKTOK_CAPTION) + """;
                textarea.dispatchEvent(new Event('input', { bubbles: true }));
                textarea.dispatchEvent(new Event('change', { bubbles: true }));
                return 'caption_set_textarea';
            }
            return 'no_caption_input';
        })()
        """)
        print(f"    Caption fill result: {fill_res}", flush=True)
        await asyncio.sleep(3)
        
        # 7. Screenshot before Post
        await session.screenshot(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\tiktok_ready_to_post.png")
        
        # 8. Click Post Button
        print("[8] Clicking Post button...", flush=True)
        post_res = await session.eval("""
        (() => {
            const btns = Array.from(document.querySelectorAll("button"));
            const postBtn = btns.find(b => b.innerText && b.innerText.trim() === 'Post');
            if (postBtn && !postBtn.hasAttribute('disabled')) {
                postBtn.click();
                return 'post_clicked';
            }
            return { error: 'post_btn_not_ready', disabled: postBtn ? postBtn.hasAttribute('disabled') : true };
        })()
        """)
        print(f"    Post result: {post_res}", flush=True)
        
        # Wait and capture final proof
        await asyncio.sleep(6)
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\tiktok_published_proof.png"
        await session.screenshot(proof_path)
        print(f"[SUCCESS] TikTok upload proof saved to: {proof_path}", flush=True)
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
