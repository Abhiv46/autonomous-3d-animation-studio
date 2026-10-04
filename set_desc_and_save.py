import asyncio
import json
from direct_cdp import DirectCDPClient, get_browser_ws

VID_ID = "X-hLtA9-VtM"

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
            if 'studio.youtube' in t.get('url', ''):
                session = await client.attach_to_target(t['targetId'])
                break
                
        if not session:
            print("Session not found!")
            return
            
        print("[1] Ensuring on edit page...")
        url = await session.eval("window.location.href")
        if f"video/{VID_ID}/edit" not in url:
            await session.eval(f"window.location.href = 'https://studio.youtube.com/video/{VID_ID}/edit'")
            await asyncio.sleep(4)
            
        # 1. Fill Description
        print("[2] Setting Description...")
        desc_res = await session.eval(f"""
        (() => {{
            const desc = document.querySelector("#description-textarea #textbox, [aria-label*='description' i]");
            if (desc) {{
                desc.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, {json.dumps(YT_DESC)});
                desc.dispatchEvent(new Event('input', {{ bubbles: true }}));
                desc.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return 'desc_inserted';
            }}
            return 'desc_box_not_found';
        }})()
        """)
        print(f"    Description set: {desc_res}")
        await asyncio.sleep(1)
        
        # 2. Add Tags
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
                tagsInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
        }})()
        """)
        await asyncio.sleep(1.5)
        
        # 3. Click Save button
        print("[4] Clicking Save button...")
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
        print(f"    Save result: {save_res}")
        await asyncio.sleep(4)
        
        # 4. Verify description text length
        check_res = await session.eval("""
        (() => {
            const desc = document.querySelector("#description-textarea #textbox, [aria-label*='description' i]");
            return desc ? desc.innerText.trim().length : 0;
        })()
        """)
        print(f"[5] Verified Description Length after Save: {check_res} chars.")
        
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_seo_confirmed_saved.png"
        await session.screenshot(proof_path)
        print("Proof screenshot saved to:", proof_path)
        
    finally:
        await client.close()

if __name__ == '__main__':
    asyncio.run(main())
