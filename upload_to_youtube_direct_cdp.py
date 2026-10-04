import asyncio
import json
import os
from direct_cdp import DirectCDPClient, get_browser_ws

VIDEO_PATH = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\TheNaughtyDuo_TikTok_RedButtonMagic_Master_CorrectSequence.mp4"

YT_TITLE = '"Red Button Ko Mat Dabana!" 🔴😱 Kaavya Ne Dabaya Phir Jo Hua... 😂🫧 #TheNaughtyDuo #shorts'

YT_DESC = """Kaartik ne baar-baar mana kiya tha — "Red Button ko bilkul mat dabana!" 🔴✋
Lekin Kaavya kahan maanne wali thi! Jaise hi Kaavya ne mysterious button dabaya... Achanak ek Giant Beach Ball unke peeche bhaagne lagi! 😱🏃‍♂️💨

Lekin ruko... machine se aakhir me kya nikla? Cute and magical bubbles! 🫧😂✨
Dekhiye Kaavya aur Kaartik ki sabse mazedaar shararat! 🥰❤️

💬 Sawaal: Aapko kya laga tha red button dabane se kya hoga? Comment me batayein! 👇

🔔 Aise hi funny 3D cartoons aur daily family adventures ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! ✨

#shorts #TheNaughtyDuo #KaavyaAndKaartik #RedButtonPrank #3DAnimation #HindiCartoon #FunnyShorts #KidsCartoon #Comedy #GiantBallChase #BubbleMachine #ViralShorts #TrendingShorts"""

YT_TAGS = [
    "The Naughty Duo", "TheNaughtyDuo", "Kaartik and Kaavya", "red button prank",
    "dont press the red button", "hindi cartoon funny", "3d animation hindi",
    "funny kids animation", "giant ball chase", "bubble machine cartoon",
    "shorts", "viral shorts 2026", "trending cartoon shorts"
]

async def main():
    ws_url = await get_browser_ws()
    print("[1] Connecting via DirectCDP...", flush=True)
    client = DirectCDPClient(ws_url)
    await client.connect()
    
    try:
        targets = await client.get_targets()
        session = None
        for t in targets:
            if t.get("type") == "page" and "studio.youtube.com" in t.get("url", ""):
                session = await client.attach_to_target(t["targetId"])
                break
                
        if not session:
            print("[!] YouTube Studio target not found!")
            return
            
        print("[2] Attached to YouTube Studio.")
        
        # 1. Click Create button
        print("[3] Clicking Create button...")
        await session.eval("""
        (() => {
            const btn = document.querySelector("#create-icon, ytcp-button#create-icon, button[aria-label*='Create' i]");
            if (btn) btn.click();
        })()
        """)
        await asyncio.sleep(1.5)
        
        # 2. Click Upload videos
        print("[4] Clicking Upload videos...")
        await session.eval("""
        (() => {
            const items = Array.from(document.querySelectorAll("ytcp-text-menu-item, tp-yt-paper-item, div"));
            const up = items.find(i => i.innerText && i.innerText.trim().toLowerCase() === 'upload videos');
            if (up) up.click();
        })()
        """)
        await asyncio.sleep(2)
        
        # 3. Locate file input via DOM
        print("[5] Locating input[type='file']...")
        await session.send("DOM.enable")
        doc = await session.send("DOM.getDocument", {"depth": -1})
        input_info = await session.send("DOM.querySelector", {
            "nodeId": doc["root"]["nodeId"],
            "selector": "input[type='file']"
        })
        input_node_id = input_info.get("nodeId")
        print(f"    Input Node ID: {input_node_id}")
        
        if not input_node_id:
            print("[!] input[type='file'] not found at root, checking dialog...")
            return
            
        # 4. Set file input
        print(f"[6] Setting file: {VIDEO_PATH}...")
        await session.send("DOM.setFileInputFiles", {
            "nodeId": input_node_id,
            "files": [VIDEO_PATH]
        })
        print("    File sent! Waiting 8s for dialog to initialize form...")
        await asyncio.sleep(8)
        
        # 5. Fill Details
        print("[7] Filling Title and Description...")
        await session.eval(f"""
        (() => {{
            // Title
            const titleBox = document.querySelector("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox");
            if (titleBox) {{
                titleBox.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, {json.dumps(YT_TITLE[:100])});
                titleBox.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
            
            // Description
            const descBox = document.querySelector("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox");
            if (descBox) {{
                descBox.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, {json.dumps(YT_DESC)});
                descBox.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
            
            // Audience: Not made for kids
            const notKidsRadio = document.querySelector("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']");
            if (notKidsRadio) notKidsRadio.click();
        }})()
        """)
        await asyncio.sleep(2)
        
        # 6. Show more & add tags
        print("[8] Adding viral tags...")
        await session.eval(f"""
        (() => {{
            const showMore = document.querySelector("#toggle-button, button[aria-label*='Show more' i]");
            if (showMore) showMore.click();
        }})()
        """)
        await asyncio.sleep(1)
        
        await session.eval(f"""
        (() => {{
            const tagsInput = document.querySelector("#tags-container input, input[aria-label='Tags'], #text-input");
            if (tagsInput) {{
                tagsInput.focus();
                const tagsStr = {json.dumps(",".join(YT_TAGS))};
                document.execCommand('insertText', false, tagsStr + ',');
                tagsInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        }})()
        """)
        await asyncio.sleep(2)
        
        proof_dir = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2"
        await session.screenshot(os.path.join(proof_dir, "yt_wizard_details_filled.png"))
        
        # 7. Wizard Next clicks
        print("[9] Stepping through Next buttons...")
        for step in range(3):
            await session.eval("""
            (() => {
                const nextBtn = document.querySelector("#next-button");
                if (nextBtn) nextBtn.click();
            })()
            """)
            await asyncio.sleep(2)
            
        # 8. Visibility: Public
        print("[10] Selecting Public visibility...")
        await session.eval("""
        (() => {
            const pubRadio = document.querySelector("tp-yt-paper-radio-button[name='PUBLIC']");
            if (pubRadio) pubRadio.click();
        })()
        """)
        await asyncio.sleep(1.5)
        
        await session.screenshot(os.path.join(proof_dir, "yt_wizard_public_ready.png"))
        
        # 9. Click Publish/Done
        print("[11] Clicking Publish/Done button...")
        await session.eval("""
        (() => {
            const doneBtn = document.querySelector("#done-button");
            if (doneBtn) doneBtn.click();
        })()
        """)
        await asyncio.sleep(6)
        
        # 10. Final screenshot
        proof_path = os.path.join(proof_dir, "yt_redbutton_published_final.png")
        await session.screenshot(proof_path)
        print(f"[SUCCESS] YouTube Short published! Proof saved to {proof_path}")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
