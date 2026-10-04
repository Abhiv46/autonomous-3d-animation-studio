import asyncio
import json
from direct_cdp import DirectCDPClient, get_browser_ws

TIKTOK_CAPTION = "Picnic Basket Bhaag Gayi! 🧺😱 Kaavya & Kaartik Ka Park Adventure! Wait for Mummy's sweet hug 🥰❤️ #TheNaughtyDuo #shorts #viral #funny #comedy #3danimation #hindicartoon #foryou #fyp #trending #toddlersoftiktok"

async def main():
    ws_url = await get_browser_ws()
    client = DirectCDPClient(ws_url)
    await client.connect()
    
    try:
        targets = await client.get_targets()
        session = None
        for t in targets:
            if t.get("type") == "page" and "tiktokstudio/upload" in t.get("url", ""):
                session = await client.attach_to_target(t["targetId"])
                break
                
        if not session:
            print("[!] TikTok Studio upload session not found!")
            return
            
        print("[1] Attached to TikTok Studio upload page.")
        
        # 1. Fill Description
        print("[2] Setting Description editor text...")
        fill_res = await session.eval(f"""
        (() => {{
            const editor = document.querySelector("div[contenteditable='true']");
            if (editor) {{
                editor.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, {json.dumps(TIKTOK_CAPTION)});
                editor.dispatchEvent(new Event('input', {{ bubbles: true }}));
                return 'caption_set';
            }}
            return 'no_editor_found';
        }})()
        """)
        print(f"    Description set result: {fill_res}")
        await asyncio.sleep(2)
        
        # Capture screenshot of ready caption
        await session.screenshot(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\tiktok_caption_filled.png")
        
        # 2. Click Post button
        print("[3] Locating and clicking Post button...")
        click_res = await session.eval("""
        (() => {
            const btns = Array.from(document.querySelectorAll("button"));
            const postBtn = btns.find(b => b.innerText && b.innerText.trim() === 'Post');
            if (postBtn) {
                postBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                postBtn.click();
                return 'clicked_post';
            }
            return 'post_btn_not_found';
        })()
        """)
        print(f"    Post click result: {click_res}")
        
        # Wait for publish confirmation
        print("[4] Waiting 8 seconds for TikTok publish processing...")
        await asyncio.sleep(8)
        
        # Capture final proof screenshot
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\tiktok_picnic_live_proof.png"
        await session.screenshot(proof_path)
        print(f"[SUCCESS] Proof screenshot saved to {proof_path}")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
