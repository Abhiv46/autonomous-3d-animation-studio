import asyncio
import json
import base64
from direct_cdp import DirectCDPClient, get_browser_ws

YT_TITLE = '"Meri Patang Atak Gayi!" 🪁😱 Mummy Ne Bachaya! 🥰😂 #TheNaughtyDuo #shorts'
YT_DESC = """Kaartik bhaiyya ki favourite laal patang hawa me udd ke unche ped par atak gayi! 🪁😱
Phir Mummy aur Kaavya ne milkar banaya ek super rescue plan! Dekhiye kya patang wapas mili? 🥰❤️

Aapki patang kabhi ped ya chatt par atki hai kya? Comment me batayein! 👇😂🪁

Aise hi cute aur funny 3D family cartoon stories ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔✨

#TheNaughtyDuo #shorts #viral #funny #kiteflying #patang #patangbazi #3danimation #hindicartoon #kidsanimation #trending #comedy #family #ytshorts"""

async def edit_draft():
    ws_url = await get_browser_ws()
    client = DirectCDPClient(ws_url)
    await client.connect()
    try:
        targets = await client.get_targets()
        session = None
        for t in targets:
            if "studio.youtube.com" in t.get("url", ""):
                session = await client.attach_to_target(t["targetId"])
                break
                
        if not session:
            print("No YT session")
            return
            
        # Click "Edit draft" button
        print("[1] Clicking 'Edit draft' button...", flush=True)
        res = await session.eval("""
        (() => {
            const btn = Array.from(document.querySelectorAll("button, ytcp-button"))
                .find(b => b.innerText && b.innerText.trim().toLowerCase() === 'edit draft');
            if (btn) {
                btn.click();
                return 'edit_draft_clicked';
            }
            return 'not_found';
        })()
        """)
        print("Edit draft result:", res, flush=True)
        await asyncio.sleep(4)
        
        # Check if dialog opened
        status = await session.eval("""
        (() => {
            const dialog = document.querySelector('ytcp-uploads-dialog');
            const titleBox = document.querySelector("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox");
            const descBox = document.querySelector("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox");
            return {
                hasDialog: !!dialog,
                hasTitleBox: !!titleBox,
                hasDescBox: !!descBox
            };
        })()
        """)
        print("[2] Dialog status after edit draft click:", status, flush=True)
        
        # Fill Title
        print("[3] Filling Title...", flush=True)
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

        # Fill Description
        print("[4] Filling Description...", flush=True)
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

        # Audience Not Made for Kids
        print("[5] Setting Audience...", flush=True)
        await session.eval("""
        (() => {
            const notKids = document.querySelector("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']");
            if (notKids) notKids.click();
        })()
        """)
        await asyncio.sleep(1)

        # Step through wizard
        print("[6] Stepping through wizard...", flush=True)
        for step in range(3):
            next_res = await session.eval("""
            (() => {
                const nextBtn = document.querySelector("ytcp-button#next-button, #next-button button");
                if (nextBtn && !nextBtn.disabled) {
                    nextBtn.click();
                    return 'clicked';
                }
                return 'disabled_or_not_found';
            })()
            """)
            print(f"    Step {step+1}: {next_res}", flush=True)
            await asyncio.sleep(2)

        # Set Visibility PUBLIC
        print("[7] Selecting PUBLIC visibility...", flush=True)
        pub_res = await session.eval("""
        (() => {
            const pubRadio = document.querySelector("ytcp-uploads-dialog tp-yt-paper-radio-button[name='PUBLIC'], tp-yt-paper-radio-button[name='PUBLIC']");
            if (pubRadio) {
                pubRadio.click();
                return 'public_selected';
            }
            return 'not_found';
        })()
        """)
        print("    Public select:", pub_res, flush=True)
        await asyncio.sleep(1.5)

        # Click Publish / Done / Save
        print("[8] Clicking Publish button...", flush=True)
        pub_btn_res = await session.eval("""
        (() => {
            const btn = document.querySelector("ytcp-uploads-dialog ytcp-button#done-button, ytcp-uploads-dialog button#publish-button, ytcp-button#done-button, ytcp-button#save-button");
            if (btn) {
                btn.click();
                return 'btn_clicked';
            }
            return 'not_found';
        })()
        """)
        print("    Publish click:", pub_btn_res, flush=True)
        await asyncio.sleep(4)

        # Check for publish anyway
        await session.eval("""
        (() => {
            const btn = Array.from(document.querySelectorAll("button, ytcp-button"))
                .find(b => b.innerText && (b.innerText.includes('Publish anyway') || b.innerText.includes('Close')));
            if (btn && btn.innerText.includes('Publish anyway')) btn.click();
        })()
        """)
        await asyncio.sleep(3)

        # Close dialog
        await session.eval("""
        (() => {
            const closeBtn = document.querySelector("ytcp-button#close-button, button[aria-label*='Close' i]");
            if (closeBtn) closeBtn.click();
        })()
        """)
        await asyncio.sleep(3)

        # Refresh shorts list
        print("[9] Refreshing Shorts list...", flush=True)
        await session.eval("window.location.href = 'https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short'")
        await asyncio.sleep(6)

        # Screenshot proof
        res = await session.send("Page.captureScreenshot", {"format": "png"})
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_kite_published_final_proof.png"
        with open(proof_path, "wb") as f:
            f.write(base64.b64decode(res["data"]))
        print(f"[SUCCESS] Final proof saved to {proof_path}!", flush=True)

    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(edit_draft())
