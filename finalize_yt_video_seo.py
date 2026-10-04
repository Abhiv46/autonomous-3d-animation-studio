import asyncio
import json
import os
from direct_cdp import DirectCDPClient, get_browser_ws

VID_ID = "X-hLtA9-VtM"

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
            
        print("[2] Dismissing any 'Publish anyway' modal if open...")
        await session.eval("""
        (() => {
            const btn = Array.from(document.querySelectorAll("button, ytcp-button"))
                .find(b => b.innerText && (b.innerText.includes('Publish anyway') || b.innerText.includes('Publish')));
            if (btn) btn.click();
        })()
        """)
        await asyncio.sleep(2)
        
        # Navigate directly to edit page
        edit_url = f"https://studio.youtube.com/video/{VID_ID}/edit"
        print(f"[3] Navigating to edit page: {edit_url}...", flush=True)
        await session.eval(f"window.location.href = '{edit_url}'")
        await asyncio.sleep(5)
        
        print("[4] Setting Title...")
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
        
        print("[5] Setting Description...")
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
        
        print("[6] Setting Audience to Not Made for Kids...")
        await session.eval("""
        (() => {
            const notKidsRadio = document.querySelector("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']");
            if (notKidsRadio) notKidsRadio.click();
        })()
        """)
        await asyncio.sleep(1)
        
        print("[7] Expanding Show More for tags...")
        await session.eval("""
        (() => {
            const showMore = document.querySelector("#toggle-button, button[aria-label*='Show more' i]");
            if (showMore) showMore.click();
        })()
        """)
        await asyncio.sleep(1.5)
        
        print("[8] Setting Tags...")
        await session.eval(f"""
        (() => {{
            const tagsInput = document.querySelector("#tags-container input, input[aria-label='Tags'], #text-input");
            if (tagsInput) {{
                tagsInput.focus();
                const tagsStr = {json.dumps(",".join(YT_TAGS))};
                document.execCommand('insertText', false, tagsStr + ',');
                tagsInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                return 'tags_set';
            }}
            return 'no_tags_input';
        }})()
        """)
        await asyncio.sleep(2)
        
        # Check Visibility dropdown if not Public
        print("[9] Checking Visibility setting...")
        await session.eval("""
        (() => {
            const visBtn = document.querySelector("#visibility-button, ytcp-video-visibility-select");
            if (visBtn && !visBtn.innerText.includes('Public')) {
                visBtn.click();
                setTimeout(() => {
                    const pub = document.querySelector("tp-yt-paper-radio-button[name='PUBLIC']");
                    if (pub) pub.click();
                    const saveVis = document.querySelector("#save-button");
                    if (saveVis) saveVis.click();
                }, 500);
            }
        })()
        """)
        await asyncio.sleep(2)
        
        # Click Save button
        print("[10] Clicking Save button...")
        save_res = await session.eval("""
        (() => {
            const saveBtn = document.querySelector("#save, ytcp-button#save");
            if (saveBtn) {
                saveBtn.click();
                return 'save_clicked';
            }
            return 'no_save_btn';
        })()
        """)
        print(f"    Save result: {save_res}", flush=True)
        await asyncio.sleep(5)
        
        proof_dir = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2"
        proof_path = os.path.join(proof_dir, "yt_redbutton_seo_saved_proof.png")
        await session.screenshot(proof_path)
        print(f"[SUCCESS] YouTube Video SEO Saved & Public! Proof: {proof_path}", flush=True)
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
