import asyncio
from direct_cdp import DirectCDPClient, get_browser_ws

VID_ID = "X-hLtA9-VtM"

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
            print("[!] YouTube Studio target not found!")
            return
            
        print("[1] Clicking 'Edit draft' button...")
        res = await session.eval("""
        (() => {
            const btn = document.querySelector("ytcp-button#edit-draft-button, button:has-text('Edit draft')");
            if (btn) {
                btn.click();
                return 'clicked_edit_draft';
            }
            // Try by text
            const allBtns = Array.from(document.querySelectorAll("button, ytcp-button"));
            const b = allBtns.find(x => x.innerText && x.innerText.trim().toLowerCase() === 'edit draft');
            if (b) {
                b.click();
                return 'clicked_by_text';
            }
            return 'no_edit_draft_btn';
        })()
        """)
        print(f"    Edit draft result: {res}")
        await asyncio.sleep(3)
        
        # Step through wizard to Visibility
        print("[2] Stepping through wizard dialog...")
        for i in range(4):
            click_next = await session.eval("""
            (() => {
                const nextBtn = document.querySelector("#next-button, ytcp-button#next-button");
                if (nextBtn && nextBtn.offsetParent !== null && !nextBtn.hasAttribute('disabled')) {
                    nextBtn.click();
                    return 'clicked_next';
                }
                return 'no_next';
            })()
            """)
            print(f"    Step {i+1} Next: {click_next}")
            await asyncio.sleep(2)
            
        # Select Public
        print("[3] Selecting Public visibility...")
        pub_res = await session.eval("""
        (() => {
            const pubRadio = document.querySelector("tp-yt-paper-radio-button[name='PUBLIC']");
            if (pubRadio) {
                pubRadio.click();
                return 'clicked_public';
            }
            return 'no_public_radio';
        })()
        """)
        print(f"    Public radio: {pub_res}")
        await asyncio.sleep(1.5)
        
        # Click Done / Publish / Save
        print("[4] Clicking Publish / Done button...")
        done_res = await session.eval("""
        (() => {
            const doneBtn = document.querySelector("#done-button, ytcp-button#done-button, #save-button");
            if (doneBtn && doneBtn.offsetParent !== null) {
                doneBtn.click();
                return 'clicked_done';
            }
            return 'no_done_btn';
        })()
        """)
        print(f"    Done button result: {done_res}")
        await asyncio.sleep(3)
        
        # Handle "Publish anyway" if popup appears
        await session.eval("""
        (() => {
            const btns = Array.from(document.querySelectorAll("button, ytcp-button"));
            const pubAnyway = btns.find(b => b.innerText && b.innerText.includes('Publish anyway'));
            if (pubAnyway) pubAnyway.click();
        })()
        """)
        await asyncio.sleep(5)
        
        # Navigate to Shorts list to take final proof
        print("[5] Navigating to Shorts channel list for proof...")
        await session.eval("window.location.href = 'https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short'")
        await asyncio.sleep(6)
        
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_redbutton_final_live_proof.png"
        await session.screenshot(proof_path)
        print(f"[SUCCESS] Final proof captured: {proof_path}")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
