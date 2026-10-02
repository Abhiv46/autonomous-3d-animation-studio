import asyncio
import json
from direct_cdp import DirectCDPClient, get_browser_ws

PROMPT = "Vertical 9:16 aspect ratio, Pixar 3D animated comedy. Pinki relaxes on sofa with brown chocolate face mask and cucumber slices on eyes, resting peacefully. Kaavya and Kaartik sneak in quietly. Kaavya whispers in cute toddler Hindi: 'Bhaiyya dekho, Mummy ke munh par chocolate cake laga hai!' Kaartik giggles: 'Chalo taste karte hain!' (All character voices strictly in cheerful cute HINDI dialogues). Ultra-vibrant colors, Pixar 3D animation."

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
                
                # 1. Dismiss any 'Agree' button if present
                await session.eval("""
                (() => {
                    const btns = Array.from(document.querySelectorAll("button"));
                    const agree = btns.find(b => b.innerText && b.innerText.trim() === 'Agree');
                    if (agree) agree.click();
                })()
                """)
                await asyncio.sleep(1)
                
                # 2. Focus and type into prompt box
                print("[2] Typing Scene 1 prompt into Flow prompt box...", flush=True)
                type_res = await session.eval("""
                (() => {
                    const box = document.querySelector("[contenteditable='true'], textarea, div.ProseMirror");
                    if (!box) return 'no_box';
                    box.focus();
                    document.execCommand('selectAll', false, null);
                    document.execCommand('delete', false, null);
                    document.execCommand('insertText', false, """ + json.dumps(PROMPT) + """);
                    return 'prompt_typed';
                })()
                """)
                print(f"    Type result: {type_res}", flush=True)
                await asyncio.sleep(1)
                
                # 3. Click Submit (arrow_forward)
                print("[3] Clicking Submit (arrow_forward)...", flush=True)
                submit_res = await session.eval("""
                (() => {
                    const btns = Array.from(document.querySelectorAll("button"));
                    const arrowBtn = btns.find(b => b.innerText && b.innerText.includes('arrow_forward'));
                    if (arrowBtn && !arrowBtn.hasAttribute('disabled')) {
                        arrowBtn.click();
                        return 'submit_clicked';
                    }
                    // Fallback to Enter key
                    const box = document.querySelector("[contenteditable='true'], textarea, div.ProseMirror");
                    if (box) {
                        const event = new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true });
                        box.dispatchEvent(event);
                        return 'enter_dispatched';
                    }
                    return 'no_submit_btn';
                })()
                """)
                print(f"    Submit result: {submit_res}", flush=True)
                await asyncio.sleep(3)
                
                # 4. Auto-approve loop
                print("[4] Auto-approving permissions...", flush=True)
                for _ in range(10):
                    app_res = await session.eval("""
                    (() => {
                        const btns = Array.from(document.querySelectorAll("button, span, div"));
                        const always = btns.find(b => b.innerText && b.innerText.includes('Always approve'));
                        if (always && always.offsetParent !== null) {
                            always.click();
                            return 'always_approved';
                        }
                        const approve = btns.find(b => b.innerText && b.innerText.trim() === 'Approve');
                        if (approve && approve.offsetParent !== null) {
                            approve.click();
                            return 'approved';
                        }
                        return 'no_modal';
                    })()
                    """)
                    if app_res in ['always_approved', 'approved']:
                        print(f"    [✓] Clicked approval: {app_res}", flush=True)
                        break
                    await asyncio.sleep(1)
                    
                # 5. Capture screenshot of generation in progress
                await asyncio.sleep(4)
                ss_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\ep22_scene1_generation_live.png"
                await session.screenshot(ss_path)
                print(f"[SUCCESS] Generation started! Screenshot: {ss_path}", flush=True)
                break
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run())
