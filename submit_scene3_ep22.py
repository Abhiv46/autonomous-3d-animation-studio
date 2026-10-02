import asyncio
import json
from direct_cdp import DirectCDPClient, get_browser_ws

SCENE3_PROMPT = "Vertical 9:16 aspect ratio, Pixar 3D comedy. Mummy wipes Kaavya's tongue with a tissue while laughing warmly, then boops Kaavya's nose with a dab of chocolate mask! All three laugh together in a warm family hug. At the end, Kaavya turns to camera with a super cute bright smile, winks, and speaks in cute toddler Hindi: 'Dosto agar maza aaya toh video ko LIKE zaroor karna aur channel ko follow aur subscribe karna! Love you!' (All character voices strictly in cheerful cute HINDI dialogues). Ultra-vibrant colors, Pixar 3D animation."

async def run():
    ws_url = await get_browser_ws()
    print("[1] Connecting to browser...", flush=True)
    client = DirectCDPClient(ws_url)
    await client.connect()
    try:
        targets = await client.get_targets()
        for t in targets:
            if t.get("type") == "page" and "flow.google.com" in t.get("url", ""):
                session = await client.attach_to_target(t["targetId"])
                
                # 1. Type Scene 3 Prompt
                print("[2] Typing Scene 3 Prompt with Cute LIKE Request CTA...", flush=True)
                type_res = await session.eval("""
                (() => {
                    const box = document.querySelector("[contenteditable='true'], textarea, div.ProseMirror");
                    if (!box) return 'no_box';
                    box.focus();
                    document.execCommand('selectAll', false, null);
                    document.execCommand('delete', false, null);
                    document.execCommand('insertText', false, """ + json.dumps(SCENE3_PROMPT) + """);
                    return 'prompt_typed';
                })()
                """)
                print(f"    Type result: {type_res}", flush=True)
                await asyncio.sleep(1)
                
                # 2. Click Submit
                print("[3] Clicking Submit...", flush=True)
                sub_res = await session.eval("""
                (() => {
                    const btns = Array.from(document.querySelectorAll("button"));
                    const arrowBtn = btns.find(b => b.innerText && b.innerText.includes('arrow_forward'));
                    if (arrowBtn && !arrowBtn.hasAttribute('disabled')) {
                        arrowBtn.click();
                        return 'submit_clicked';
                    }
                    return 'no_btn';
                })()
                """)
                print(f"    Submit result: {sub_res}", flush=True)
                await asyncio.sleep(3)
                
                # 3. Auto-approve
                for _ in range(8):
                    app = await session.eval("""
                    (() => {
                        const btns = Array.from(document.querySelectorAll("button, span, div"));
                        const always = btns.find(b => b.innerText && b.innerText.includes('Always approve'));
                        if (always && always.offsetParent !== null) { always.click(); return 'always_approved'; }
                        const approve = btns.find(b => b.innerText && b.innerText.trim() === 'Approve');
                        if (approve && approve.offsetParent !== null) { approve.click(); return 'approved'; }
                        return null;
                    })()
                    """)
                    if app:
                        print(f"    [✓] Auto-approved: {app}", flush=True)
                        break
                    await asyncio.sleep(1)
                    
                print("[SUCCESS] Scene 3 submitted with cute LIKE CTA!", flush=True)
                break
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run())
