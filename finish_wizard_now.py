import asyncio
import json
import os
from direct_cdp import DirectCDPClient, get_browser_ws

YT_DESC = """Kaartik ne baar-baar mana kiya tha — "Red Button ko bilkul mat dabana!" 🔴✋
Lekin Kaavya kahan maanne wali thi! Jaise hi Kaavya ne mysterious button dabaya... Achanak ek Giant Beach Ball unke peeche bhaagne lagi! 😱🏃‍♂️💨

Lekin ruko... machine se aakhir me kya nikla? Cute and magical bubbles! 🫧😂✨
Dekhiye Kaavya aur Kaartik ki sabse mazedaar shararat! 🥰❤️

💬 Sawaal: Aapko kya laga tha red button dabane se kya hoga? Comment me batayein! 👇

🔔 Aise hi funny 3D cartoons aur daily family adventures ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! ✨

#shorts #TheNaughtyDuo #KaavyaAndKaartik #RedButtonPrank #3DAnimation #HindiCartoon #FunnyShorts #KidsCartoon #Comedy #GiantBallChase #BubbleMachine #ViralShorts #TrendingShorts"""

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
            print("Session not found!")
            return
            
        print("[1] Filling Description if needed...")
        await session.eval(f"""
        (() => {{
            const descBox = document.querySelector("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox");
            if (descBox && (!descBox.innerText || descBox.innerText.trim().length === 0)) {{
                descBox.focus();
                document.execCommand('insertText', false, {json.dumps(YT_DESC)});
                descBox.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        }})()
        """)
        await asyncio.sleep(1.5)
        
        # Click Next through the 3 steps
        print("[2] Stepping Next...")
        for i in range(3):
            res = await session.eval("""
            (() => {
                const nextBtn = document.querySelector("#next-button, ytcp-button#next-button");
                if (nextBtn) {
                    nextBtn.click();
                    return 'clicked_next';
                }
                return 'no_next';
            })()
            """)
            print(f"    Next step {i+1}: {res}")
            await asyncio.sleep(2)
            
        # Select Public
        print("[3] Selecting Public visibility...")
        pub_res = await session.eval("""
        (() => {
            const pub = document.querySelector("tp-yt-paper-radio-button[name='PUBLIC']");
            if (pub) {
                pub.click();
                return 'clicked_public';
            }
            return 'no_public';
        })()
        """)
        print(f"    Public result: {pub_res}")
        await asyncio.sleep(1.5)
        
        # Click Done/Save
        print("[4] Clicking Done/Save/Publish button...")
        done_res = await session.eval("""
        (() => {
            const done = document.querySelector("#done-button, ytcp-button#done-button, #save-button");
            if (done) {
                done.click();
                return 'clicked_done';
            }
            return 'no_done';
        })()
        """)
        print(f"    Done result: {done_res}")
        await asyncio.sleep(3)
        
        # Publish anyway popup if any
        await session.eval("""
        (() => {
            const btns = Array.from(document.querySelectorAll("button, ytcp-button"));
            const pub = btns.find(b => b.innerText && b.innerText.includes('Publish anyway'));
            if (pub) pub.click();
        })()
        """)
        await asyncio.sleep(5)
        
        # Navigate to Shorts list
        print("[5] Navigating to Shorts channel list...")
        await session.eval("window.location.href = 'https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short'")
        await asyncio.sleep(6)
        
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_final_published_public_proof.png"
        await session.screenshot(proof_path)
        print(f"[SUCCESS] Proof captured: {proof_path}")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
