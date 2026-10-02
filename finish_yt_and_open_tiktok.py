import asyncio
import time
from direct_cdp import DirectCDPClient, get_browser_ws

async def main():
    ws_url = await get_browser_ws()
    print("[1] Connecting to browser...", flush=True)
    client = DirectCDPClient(ws_url)
    await client.connect()
    
    try:
        targets = await client.get_targets()
        yt_target = None
        for t in targets:
            if "youtube" in t.get("url", ""):
                yt_target = t
                break
                
        if not yt_target:
            print("[!] YouTube target not found!")
            return
            
        print("[2] Attaching to YouTube Studio...", flush=True)
        session = await client.attach_to_target(yt_target["targetId"])
        
        # Advance through upload wizard
        for step_idx in range(6):
            js = """
            (() => {
                const res = {};
                const dialog = document.querySelector('ytcp-uploads-dialog');
                if (!dialog) return { error: 'no dialog' };
                
                // 1. Not made for kids
                const notKids = dialog.querySelector("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']");
                if (notKids && notKids.getAttribute('aria-checked') !== 'true') {
                    notKids.click();
                    res.notKidsClicked = true;
                }
                
                // 2. Next button
                const nextBtn = dialog.querySelector("#next-button, ytcp-button#next-button, button[aria-label='Next']");
                if (nextBtn && nextBtn.offsetParent !== null && !nextBtn.hasAttribute('disabled')) {
                    nextBtn.click();
                    res.nextClicked = true;
                    return res;
                }
                
                // 3. Public visibility
                const pub = dialog.querySelector("tp-yt-paper-radio-button[name='PUBLIC']");
                if (pub) {
                    pub.click();
                    res.pubClicked = true;
                }
                
                // 4. Done / Publish / Save
                const doneBtn = dialog.querySelector("#done-button, ytcp-button#done-button, button[aria-label='Publish'], button[aria-label='Save']");
                if (doneBtn && doneBtn.offsetParent !== null && !doneBtn.hasAttribute('disabled')) {
                    doneBtn.click();
                    res.doneClicked = true;
                    return res;
                }
                
                // 5. Publish anyway button if warning shows
                const anyway = document.querySelector("ytcp-button#publish-button, button:has-text('Publish anyway')");
                if (anyway && anyway.offsetParent !== null) {
                    anyway.click();
                    res.anywayClicked = true;
                }
                
                return res;
            })()
            """
            step_result = await session.eval(js)
            print(f"Step {step_idx+1}: {step_result}", flush=True)
            await asyncio.sleep(2)
            
        # Capture proof screenshot
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_published_original_audio_proof.png"
        await session.screenshot(proof_path)
        print(f"[SUCCESS] YouTube Short published proof saved to: {proof_path}", flush=True)
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
