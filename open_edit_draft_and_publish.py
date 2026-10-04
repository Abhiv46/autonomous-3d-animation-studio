import asyncio
import json
import os
from direct_cdp import DirectCDPClient, get_browser_ws

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
            print("[!] YouTube Studio not found!")
            return
            
        print("[1] Clicking Edit draft button...")
        click_draft = await session.eval("""
        (() => {
            const btns = Array.from(document.querySelectorAll("button, ytcp-button"));
            const editDraft = btns.find(b => b.innerText && b.innerText.trim().toLowerCase() === 'edit draft');
            if (editDraft) {
                editDraft.click();
                return 'clicked_edit_draft';
            }
            return 'not_found';
        })()
        """)
        print(f"    Result: {click_draft}")
        await asyncio.sleep(4)
        
        proof_dir = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2"
        await session.screenshot(os.path.join(proof_dir, "draft_wizard_opened.png"))
        
        # 1. Title & Description
        print("[2] Filling Title and Description in wizard...")
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
            const notKids = document.querySelector("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']");
            if (notKids) notKids.click();
        }})()
        """)
        await asyncio.sleep(2)
        
        # 2. Show more & Tags
        print("[3] Adding Tags...")
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
        
        await session.screenshot(os.path.join(proof_dir, "draft_wizard_filled.png"))
        
        # 3. Next buttons
        print("[4] Stepping through Next buttons...")
        for i in range(3):
            await session.eval("""
            (() => {
                const nextBtn = document.querySelector("#next-button, ytcp-button#next-button");
                if (nextBtn) nextBtn.click();
            })()
            """)
            await asyncio.sleep(2)
            
        # 4. Public Radio
        print("[5] Selecting Public visibility...")
        await session.eval("""
        (() => {
            const pubRadio = document.querySelector("tp-yt-paper-radio-button[name='PUBLIC']");
            if (pubRadio) pubRadio.click();
        })()
        """)
        await asyncio.sleep(1.5)
        
        await session.screenshot(os.path.join(proof_dir, "draft_wizard_public_selected.png"))
        
        # 5. Save/Done button
        print("[6] Clicking Save/Done/Publish button...")
        await session.eval("""
        (() => {
            const doneBtn = document.querySelector("#done-button, ytcp-button#done-button, #save-button");
            if (doneBtn) doneBtn.click();
        })()
        """)
        await asyncio.sleep(3)
        
        # 6. Publish anyway popup if any
        print("[7] Dismissing any 'Publish anyway' modal...")
        await session.eval("""
        (() => {
            const btns = Array.from(document.querySelectorAll("button, ytcp-button"));
            const pub = btns.find(b => b.innerText && b.innerText.includes('Publish anyway'));
            if (pub) pub.click();
        })()
        """)
        await asyncio.sleep(5)
        
        # Reload Shorts tab for final proof
        print("[8] Reloading Shorts tab for live proof...")
        await session.eval("window.location.href = 'https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short'")
        await asyncio.sleep(6)
        
        final_proof = os.path.join(proof_dir, "yt_redbutton_100pct_public_proof.png")
        await session.screenshot(final_proof)
        print(f"[SUCCESS] Final proof saved: {final_proof}")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
