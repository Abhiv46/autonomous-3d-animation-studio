import asyncio
import json
from direct_cdp import DirectCDPClient, get_browser_ws

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
                
        if not session:
            print("[!] YouTube target not found!")
            return

        status = await session.eval("""
        (() => {
            const dialog = document.querySelector('ytcp-uploads-dialog');
            const title = document.querySelector("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox");
            const nextBtn = document.querySelector('ytcp-button#next-button, #next-button button');
            const pubBtn = document.querySelector('ytcp-uploads-dialog ytcp-button#done-button, ytcp-uploads-dialog button#publish-button');
            const links = Array.from(document.querySelectorAll("a")).map(a => a.href).filter(h => h.includes("youtu.be") || h.includes("shorts"));
            return {
                hasDialog: !!dialog,
                title: title ? title.innerText : null,
                hasNext: !!nextBtn,
                nextDisabled: nextBtn ? nextBtn.disabled : null,
                hasPub: !!pubBtn,
                links: links
            };
        })()
        """)
        print("[+] Current Dialog Status:", status, flush=True)

        # Step through wizard
        for step in range(3):
            res = await session.eval("""
            (() => {
                const nextBtn = document.querySelector("ytcp-button#next-button, #next-button button");
                if (nextBtn && !nextBtn.disabled) {
                    nextBtn.click();
                    return 'clicked';
                }
                return 'disabled_or_not_found';
            })()
            """)
            print(f"    Next click {step+1}: {res}", flush=True)
            await asyncio.sleep(2)

        # Visibility PUBLIC
        print("[+] Selecting PUBLIC visibility...", flush=True)
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

        # Click Publish / Done
        print("[+] Clicking Publish button...", flush=True)
        publish_res = await session.eval("""
        (() => {
            const doneBtn = document.querySelector("ytcp-uploads-dialog ytcp-button#done-button, ytcp-uploads-dialog button#publish-button, ytcp-button#done-button");
            if (doneBtn) {
                doneBtn.click();
                return 'done_clicked';
            }
            return 'not_found';
        })()
        """)
        print("    Publish click:", publish_res, flush=True)
        await asyncio.sleep(4)

        # Publish anyway if shown
        anyway = await session.eval("""
        (() => {
            const btn = Array.from(document.querySelectorAll("button, ytcp-button"))
                .find(b => b.innerText && (b.innerText.includes('Publish anyway') || b.innerText.includes('Close')));
            if (btn && btn.innerText.includes('Publish anyway')) {
                btn.click();
                return 'publish_anyway_clicked';
            }
            return 'no_anyway';
        })()
        """)
        print("    Publish anyway:", anyway, flush=True)
        await asyncio.sleep(3)

        # Close dialog
        await session.eval("""
        (() => {
            const closeBtn = document.querySelector("ytcp-button#close-button, button[aria-label*='Close' i]");
            if (closeBtn) closeBtn.click();
        })()
        """)
        await asyncio.sleep(3)

        print("[SUCCESS] Published kite video to YouTube Shorts!", flush=True)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run())
