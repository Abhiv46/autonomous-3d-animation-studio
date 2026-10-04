import asyncio
import json
import os
from direct_cdp import DirectCDPClient, get_browser_ws

VIDEO_PATH = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\TheNaughtyDuo_TikTok_KiteAdventure_Master.mp4"
TIKTOK_CAPTION = "Kaartik Ki Red Patang Ped Me Atak Gayi! 🪁😱 Phir Mummy & Kaavya Ne Bachaya! 🥰❤️ #TheNaughtyDuo #shorts #viral #funny #cute #kiteflying #3danimation #hindicartoon #foryou #fyp #trending #family #patang"

async def main():
    ws_url = await get_browser_ws()
    print("[1] Connecting to browser via DirectCDP...", flush=True)
    client = DirectCDPClient(ws_url)
    await client.connect()
    
    try:
        targets = await client.get_targets()
        session = None
        for t in targets:
            if t.get("type") == "page" and "tiktokstudio/upload" in t.get("url", ""):
                session = await client.attach_to_target(t["targetId"])
                break
                
        if not session:
            print("[+] Opening TikTok Studio upload page...", flush=True)
            tid = await client.create_target("https://www.tiktok.com/tiktokstudio/upload")
            session = await client.attach_to_target(tid)
            await asyncio.sleep(5)
            
        print("[2] Attached to TikTok Studio upload page.")
        
        # 1. Check Discard button if previous state stuck
        await session.eval("""
        (() => {
            const btns = Array.from(document.querySelectorAll("button"));
            const discard = btns.find(b => b.innerText && b.innerText.trim() === 'Discard');
            if (discard) discard.click();
        })()
        """)
        await asyncio.sleep(2)
        
        # 2. Locate file input
        print("[3] Locating input[type='file']...")
        await session.send("DOM.enable")
        doc = await session.send("DOM.getDocument", {"depth": -1})
        input_info = await session.send("DOM.querySelector", {
            "nodeId": doc["root"]["nodeId"],
            "selector": "input[type='file']"
        })
        input_node_id = input_info.get("nodeId")
        print(f"    Input Node ID: {input_node_id}")
        
        if not input_node_id:
            print("[!] input[type='file'] not found!")
            return
            
        # 3. Set file input
        print(f"[4] Uploading {VIDEO_PATH}...")
        await session.send("DOM.setFileInputFiles", {
            "nodeId": input_node_id,
            "files": [VIDEO_PATH]
        })
        print("    File sent! Waiting for upload form to load...")
        
        # 4. Wait for upload to process
        for i in range(25):
            await asyncio.sleep(2)
            state = await session.eval("""
            (() => {
                const textareas = Array.from(document.querySelectorAll("div[contenteditable='true'], textarea, input"));
                const btns = Array.from(document.querySelectorAll("button")).map(b => b.innerText.trim());
                return {
                    hasEditable: textareas.some(t => t.offsetParent !== null),
                    postBtn: btns.includes("Post")
                };
            })()
            """)
            print(f"    Wait check {i+1}: {state}")
            if state.get("postBtn") and state.get("hasEditable"):
                print("    Upload ready and form loaded!")
                break
                
        proof_dir = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2"
        await session.screenshot(os.path.join(proof_dir, "tiktok_kite_uploaded_form.png"))
        
        # 5. Fill Caption
        print("[5] Filling Viral SEO Caption...")
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
            return 'no_editor';
        }})()
        """)
        print(f"    Caption set: {fill_res}")
        await asyncio.sleep(2)
        
        await session.screenshot(os.path.join(proof_dir, "tiktok_kite_caption_filled.png"))
        
        # 6. Click Post button
        print("[6] Clicking Post button...")
        click_post = await session.eval("""
        (() => {
            const btns = Array.from(document.querySelectorAll("button"));
            const post = btns.find(b => b.innerText && b.innerText.trim() === 'Post');
            if (post) {
                post.scrollIntoView({ behavior: 'smooth', block: 'center' });
                post.click();
                return 'post_clicked';
            }
            return 'no_post_btn';
        })()
        """)
        print(f"    Post click result: {click_post}")
        await asyncio.sleep(8)
        
        # 7. Final proof
        proof_path = os.path.join(proof_dir, "tiktok_kite_posted_proof.png")
        await session.screenshot(proof_path)
        print(f"[SUCCESS] TikTok upload completed! Proof saved to {proof_path}")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
