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

async def run():
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
                
        # 1. Fill Description
        print("[1] Setting Description in dialog...", flush=True)
        set_desc = await session.eval(f"""
        (() => {{
            const diag = document.querySelector('ytcp-uploads-dialog');
            const descBox = diag.querySelector("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox");
            if (descBox) {{
                descBox.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, {json.dumps(YT_DESC)});
                descBox.dispatchEvent(new Event('input', {{ bubbles: true }}));
                return 'desc_filled';
            }}
            return 'no_desc_box';
        }})()
        """)
        print("    Desc result:", set_desc, flush=True)
        await asyncio.sleep(1)

        # 2. Select Not Made for Kids
        print("[2] Selecting Not Made for Kids...", flush=True)
        set_kids = await session.eval("""
        (() => {
            const diag = document.querySelector('ytcp-uploads-dialog');
            const notKids = diag.querySelector("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']");
            if (notKids) {
                notKids.click();
                return 'not_kids_clicked';
            }
            return 'no_radio';
        })()
        """)
        print("    Not kids result:", set_kids, flush=True)
        await asyncio.sleep(1)

        # 3. Click Visibility tab directly (step-badge-3)
        print("[3] Clicking Visibility step badge...", flush=True)
        click_step3 = await session.eval("""
        (() => {
            const diag = document.querySelector('ytcp-uploads-dialog');
            const badge3 = diag.querySelector('#step-badge-3, button#step-badge-3');
            if (badge3) {
                badge3.click();
                return 'badge3_clicked';
            }
            return 'no_badge3';
        })()
        """)
        print("    Step badge 3 click:", click_step3, flush=True)
        await asyncio.sleep(2)

        # 4. Check Visibility options
        print("[4] Selecting PUBLIC radio button...", flush=True)
        sel_pub = await session.eval("""
        (() => {
            const diag = document.querySelector('ytcp-uploads-dialog');
            const pubRadio = diag.querySelector("tp-yt-paper-radio-button[name='PUBLIC']");
            if (pubRadio) {
                pubRadio.click();
                return 'pub_clicked';
            }
            return 'no_pub_radio';
        })()
        """)
        print("    Public select:", sel_pub, flush=True)
        await asyncio.sleep(1.5)

        # 5. Click Done / Save button
        print("[5] Clicking Save / Publish button...", flush=True)
        click_done = await session.eval("""
        (() => {
            const diag = document.querySelector('ytcp-uploads-dialog');
            const doneBtn = diag.querySelector('ytcp-button#done-button, button#done-button');
            if (doneBtn) {
                doneBtn.click();
                return 'done_clicked';
            }
            return 'no_done_btn';
        })()
        """)
        print("    Done click:", click_done, flush=True)
        await asyncio.sleep(4)

        # 6. Check Publish anyway
        anyway = await session.eval("""
        (() => {
            const btn = Array.from(document.querySelectorAll("button, ytcp-button"))
                .find(b => b.innerText && (b.innerText.includes('Publish anyway') || b.innerText.includes('Close')));
            if (btn && btn.innerText.includes('Publish anyway')) {
                btn.click();
                return 'anyway_clicked';
            }
            return 'no_anyway';
        })()
        """)
        print("    Anyway check:", anyway, flush=True)
        await asyncio.sleep(3)

        # 7. Close dialog if close button visible
        await session.eval("""
        (() => {
            const btn = document.querySelector("ytcp-button#close-button, button[aria-label*='Close' i]");
            if (btn) btn.click();
        })()
        """)
        await asyncio.sleep(2)

        # 8. Reload / Go to shorts list
        print("[8] Navigating to Shorts channel list...", flush=True)
        await session.eval("window.location.href = 'https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short'")
        await asyncio.sleep(5)

        # Screenshot proof
        res = await session.send("Page.captureScreenshot", {"format": "png"})
        proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_kite_public_success.png"
        with open(proof, "wb") as f:
            f.write(base64.b64decode(res["data"]))
        print(f"[SUCCESS] Proof saved to {proof}!", flush=True)

    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run())
