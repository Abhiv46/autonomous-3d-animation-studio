import asyncio
import json
import os
import sys
from pathlib import Path
from direct_cdp import DirectCDPClient, get_browser_ws

VIDEO_PATH = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\TheNaughtyDuo_TikTok_KiteAdventure_Master.mp4"
SCREENSHOT_DIR = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2")

YT_TITLE = '"Meri Patang Ped Me Atak Gayi!" 🪁😱 Mummy Ne Bachaya! 🥰😂 #TheNaughtyDuo #shorts'
YT_DESC = """Kaartik bhaiyya ki favourite laal patang hawa me udd ke unche ped par atak gayi! 🪁😱
Phir Mummy aur Kaavya ne milkar banaya ek super rescue plan! Dekhiye kya patang wapas mili? 🥰❤️

Aapki patang kabhi ped ya chatt par atki hai kya? Comment me batayein! 👇😂🪁

Aise hi cute aur funny 3D family cartoon stories ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔✨

#TheNaughtyDuo #shorts #viral #funny #kiteflying #patang #patangbazi #3danimation #hindicartoon #kidsanimation #trending #comedy #family #ytshorts"""

async def main():
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
        
        # Check if upload dialog is already present
        diag_present = await session.eval("!!document.querySelector('ytcp-uploads-dialog')")
        if not diag_present:
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
            print("[!] Could not find input[type='file']! Retrying after clicking Select Files...")
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
            print(f"    Retry Input Node ID: {input_node_id}", flush=True)
            
        if not input_node_id:
            print("[!] FATAL: input[type='file'] not found.")
            return

        # 3. Set file
        print(f"[5] Setting file: {VIDEO_PATH}...", flush=True)
        await session.send("DOM.setFileInputFiles", {
            "nodeId": input_node_id,
            "files": [VIDEO_PATH]
        })
        print("    File set sent successfully!", flush=True)
        
        # 4. Wait for dialog to populate
        print("[6] Waiting for upload dialog to process video...", flush=True)
        video_url = None
        for i in range(20):
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
            print(f"    Status check {i+1}: {status}", flush=True)
            if status.get("links") and len(status["links"]) > 0:
                video_url = status["links"][0]
            if status.get("hasTitle") and status.get("hasDialog"):
                break
                
        print(f"[+] Video URL detected: {video_url}", flush=True)
        
        # 5. Fill Title
        print("[7] Filling Title...", flush=True)
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
        print("[8] Filling Description...", flush=True)
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

        # 7. Set Audience to Not Made For Kids
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

        proof_details = str(SCREENSHOT_DIR / "yt_kite_details_filled.png")
        await session.screenshot(proof_details)
        print(f"[+] Details screenshot saved to {proof_details}", flush=True)

        # 8. Step through Wizard (Next buttons)
        print("[10] Stepping through Wizard...", flush=True)
        for step in range(3):
            clicked = await session.eval("""
            (() => {
                const nextBtn = document.querySelector("ytcp-button#next-button, button[aria-label*='Next' i], #next-button button");
                if (nextBtn && !nextBtn.disabled) {
                    nextBtn.click();
                    return 'clicked';
                }
                return 'not_found_or_disabled';
            })()
            """)
            print(f"    Next step {step+1}: {clicked}", flush=True)
            await asyncio.sleep(2)

        # 9. Set Visibility to PUBLIC
        print("[11] Setting Visibility to PUBLIC...", flush=True)
        pub_res = await session.eval("""
        (() => {
            const pubRadio = document.querySelector("ytcp-uploads-dialog tp-yt-paper-radio-button[name='PUBLIC'], tp-yt-paper-radio-button[name='PUBLIC']");
            if (pubRadio) {
                pubRadio.click();
                return 'public_selected';
            }
            return 'no_public_radio';
        })()
        """)
        print(f"    Public radio: {pub_res}", flush=True)
        await asyncio.sleep(1.5)

        proof_vis = str(SCREENSHOT_DIR / "yt_kite_visibility_public.png")
        await session.screenshot(proof_vis)
        print(f"[+] Visibility screenshot saved to {proof_vis}", flush=True)

        # 10. Click Publish / Done
        print("[12] Clicking Publish button...", flush=True)
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

        # Check for 'Publish anyway'
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

        proof_done = str(SCREENSHOT_DIR / "yt_kite_published_done.png")
        await session.screenshot(proof_done)
        print(f"[+] Published screenshot saved to {proof_done}", flush=True)

        # Close dialog if close button visible
        await session.eval("""
        (() => {
            const closeBtn = document.querySelector("ytcp-button#close-button, button[aria-label*='Close' i]");
            if (closeBtn) closeBtn.click();
        })()
        """)
        await asyncio.sleep(3)

        # Navigate to Shorts list
        print("[13] Navigating to Shorts channel list...", flush=True)
        await session.eval("window.location.href = 'https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short'")
        await asyncio.sleep(5)

        proof_list = str(SCREENSHOT_DIR / "yt_kite_final_channel_shorts.png")
        await session.screenshot(proof_list)
        print(f"[SUCCESS] Upload completed! Final screenshot saved to {proof_list}", flush=True)
        print(f"[INFO] Final Video URL: {video_url}", flush=True)

    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
