import asyncio
import json
import os
from direct_cdp import DirectCDPClient, get_browser_ws

VIDEO_PATH = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\TheNaughtyDuo_TikTok_RedButtonMagic_Master_CorrectSequence.mp4"

async def main():
    ws_url = await get_browser_ws()
    print("[1] Connecting via DirectCDP...", flush=True)
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
        
        # 2. Find file input
        print("[4] Finding input[type='file']...", flush=True)
        await session.send("DOM.enable")
        doc = await session.send("DOM.getDocument", {"depth": -1})
        input_info = await session.send("DOM.querySelector", {
            "nodeId": doc["root"]["nodeId"],
            "selector": "input[type='file']"
        })
        input_node_id = input_info.get("nodeId")
        print(f"    Input Node ID: {input_node_id}", flush=True)
        
        if not input_node_id:
            print("[!] Could not find input[type='file']!")
            return
            
        # 3. Set file
        print(f"[5] Setting file {VIDEO_PATH}...", flush=True)
        await session.send("DOM.setFileInputFiles", {
            "nodeId": input_node_id,
            "files": [VIDEO_PATH]
        })
        print("    File set sent successfully!", flush=True)
        
        # Wait 8s for dialog to process
        print("[6] Waiting for upload dialog to initialize...", flush=True)
        for i in range(15):
            await asyncio.sleep(2)
            diag_state = await session.eval("""
            (() => {
                const dialog = document.querySelector("ytcp-uploads-dialog");
                const titleInput = document.querySelector("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox");
                const links = Array.from(document.querySelectorAll("a")).map(a => a.href).filter(h => h.includes("youtu.be") || h.includes("shorts"));
                return {
                    hasDialog: !!dialog,
                    hasTitle: !!titleInput,
                    links: links
                };
            })()
            """)
            print(f"    Wait check {i+1}: {diag_state}", flush=True)
            if diag_state.get("hasTitle") or diag_state.get("links"):
                break
                
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_direct_cdp_upload_ready.png"
        await session.screenshot(proof_path)
        print(f"[+] Screenshot saved to {proof_path}", flush=True)
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
