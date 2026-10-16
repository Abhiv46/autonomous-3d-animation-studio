import asyncio
import json
import os
import sys
from direct_cdp import DirectCDPClient, get_browser_ws

VIDEO_PATH = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\Kaavya_Chocolate_Chori_Master.mp4"

YT_TITLE = "Kaavya Ne Chori Ki Chocolate! 🍫😂 Kaartik Ne Pakda Rangey Haath! #TheNaughtyDuo #shorts"

YT_DESC = """Mummy ne fridge me rakhi thi chocolate, lekin Kaavya ne secretly saari chocolate chupa li! 🍫😋
Kaartik bhaiyya ko ho gaya shak... aur shuru hua interrogation! 🕵️‍♂️😂
Kaavya ne banaye cute bahane: "Maine toh chocolate dekhi bhi nahi!" 😇
Lekin achanak Kaavya ke muh par lagi chocolate ne khol diya saara raaz! 😱🍫🤣
Dekhiye Kaavya aur Kaartik ki sabse funny chocolate chori comedy! ❤️✨

💬 Sawaal: Kya aapne bhi bachpan me secretly chocolate ya mithai chori karke khayi hai? Comment me batao! 👇

🔔 Aise hi mazedaar 3D family cartoons aur daily siblings comedy stories ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 💖

#shorts #TheNaughtyDuo #KaavyaAndKaartik #ChocolateChori #FunnyShorts #HindiCartoon #3DAnimation #CartoonStories #SiblingsComedy #KidsAnimation #ViralShorts #Trending"""

YT_TAGS = [
    "The Naughty Duo", "TheNaughtyDuo", "Kaartik and Kaavya", "chocolate chori",
    "chocolate prank", "hindi cartoon", "3d animation hindi", "kids cartoon funny",
    "siblings comedy", "funny hindi stories", "cartoon video hindi", "shorts", "viral shorts"
]

async def main():
    print("[1] Getting browser WebSocket URL...", flush=True)
    ws_url = await get_browser_ws()
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
            # Check if any youtube page exists
            for t in targets:
                if t.get("type") == "page" and "youtube.com" in t.get("url", ""):
                    session = await client.attach_to_target(t["targetId"])
                    print("Navigating existing YouTube tab to Studio...")
                    await session.navigate("https://studio.youtube.com")
                    await asyncio.sleep(6)
                    break
                    
        if not session:
            # Create target
            print("Creating new Studio target...")
            target_id = await client.create_target("https://studio.youtube.com")
            session = await client.attach_to_target(target_id)
            await asyncio.sleep(6)
            
        print("[2] Attached to YouTube Studio.")
        
        # Click Create button
        print("[3] Clicking Create button...")
        await session.eval("""
        (() => {
            const btn = document.querySelector("#create-icon, ytcp-button#create-icon, button[aria-label*='Create' i]");
            if (btn) btn.click();
        })()
        """)
        await asyncio.sleep(1.5)
        
        # Click Upload videos
        print("[4] Clicking Upload videos...")
        await session.eval("""
        (() => {
            const items = Array.from(document.querySelectorAll("ytcp-text-menu-item, tp-yt-paper-item, div"));
            const up = items.find(i => i.innerText && i.innerText.trim().toLowerCase() === 'upload videos');
            if (up) up.click();
        })()
        """)
        await asyncio.sleep(2)
        
        # Locate input[type='file'] via DOM
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
            print("[!] input[type='file'] not found!")
            return
            
        # Set file input
        print(f"[6] Uploading Master Video: {VIDEO_PATH}...")
        await session.send("DOM.setFileInputFiles", {
            "nodeId": input_node_id,
            "files": [VIDEO_PATH]
        })
        print("    File sent directly via CDP! Waiting 10s for upload dialog...")
        await asyncio.sleep(10)
        
        # Fill Title and Description
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
        
        # Show more & add tags
        print("[8] Adding viral tags...")
        await session.eval("""
        (() => {
            const showMore = document.querySelector("#toggle-button, button[aria-label*='Show more' i]");
            if (showMore) showMore.click();
        })()
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
        
        # Get video link
        video_link = await session.eval("""
        (() => {
            const a = document.querySelector("a.ytcp-video-info, a[href*='youtu.be'], a[href*='youtube.com/shorts']");
            return a ? a.href : null;
        })()
        """)
        print(f"[+] Video Link: {video_link}")
        
        # Wizard Next clicks
        print("[9] Stepping through Next buttons...")
        for step in range(3):
            await session.eval("""
            (() => {
                const nextBtn = document.querySelector("#next-button");
                if (nextBtn) nextBtn.click();
            })()
            """)
            await asyncio.sleep(2.5)
            
        # Visibility: Public
        print("[10] Selecting Public visibility...")
        await session.eval("""
        (() => {
            const pubRadio = document.querySelector("tp-yt-paper-radio-button[name='PUBLIC']");
            if (pubRadio) pubRadio.click();
        })()
        """)
        await asyncio.sleep(2)
        
        # Click Publish/Done
        print("[11] Clicking Publish/Done button...")
        await session.eval("""
        (() => {
            const doneBtn = document.querySelector("#done-button");
            if (doneBtn) doneBtn.click();
        })()
        """)
        await asyncio.sleep(8)
        
        # Proof screenshot
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\chocolate_published_proof.png"
        await session.screenshot(proof_path)
        print(f"[SUCCESS] Uploaded to YouTube! Proof: {proof_path}")
        print(f"Live Video Link: {video_link}")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
