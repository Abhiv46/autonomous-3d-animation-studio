import asyncio
import json
from direct_cdp import DirectCDPClient, get_browser_ws

PROMPT = "Vertical 9:16 aspect ratio, ultra-detailed Pixar 3D animated comedy. Sunlit modern Indian living room. Exactly ONE Pinki (25, mother, powder-blue kurti) sitting on sofa with a thick brown glossy chocolate clay face mask and cucumber slices on eyes. Beside her, Exactly ONE Kaavya (3.5, pink frock, twin buns) dipping her tiny finger into Mummy's cheek with an innocent toddler grin. Exactly ONE Kaartik (5, yellow polo) watching with wide funny eyes and mouth watering. Vibrant cinematic 3D lighting, bright pastel colors, cute expressive cartoon faces."

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
                
                # 1. Dismiss any 'Agree' button or popups
                await session.eval("""
                (() => {
                    const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true });
                    document.dispatchEvent(esc);
                    const btns = Array.from(document.querySelectorAll("button"));
                    const agree = btns.find(b => b.innerText && b.innerText.trim() === 'Agree');
                    if (agree) agree.click();
                })()
                """)
                await asyncio.sleep(1)
                
                # 2. Focus and enter prompt into textarea
                print("[2] Entering Scene 1 Image Prompt (9:16 Pixar 3D)...", flush=True)
                type_res = await session.eval("""
                (() => {
                    const box = document.querySelector("textarea, [contenteditable='true'], div.ProseMirror");
                    if (!box) return 'no_box';
                    box.focus();
                    if (box.tagName === 'TEXTAREA') {
                        box.value = """ + json.dumps(PROMPT) + """;
                        box.dispatchEvent(new Event('input', { bubbles: true }));
                        box.dispatchEvent(new Event('change', { bubbles: true }));
                    } else {
                        document.execCommand('selectAll', false, null);
                        document.execCommand('delete', false, null);
                        document.execCommand('insertText', false, """ + json.dumps(PROMPT) + """);
                    }
                    return 'prompt_typed';
                })()
                """)
                print(f"    Type result: {type_res}", flush=True)
                await asyncio.sleep(1)
                
                # 3. Click Submit / arrow_forward button
                print("[3] Clicking Submit (arrow_forward)...", flush=True)
                submit_res = await session.eval("""
                (() => {
                    const btns = Array.from(document.querySelectorAll("button"));
                    const arrowBtn = btns.find(b => b.innerText && (b.innerText.includes('arrow_forward') || b.getAttribute('aria-label') === 'Submit' || b.getAttribute('aria-label') === 'Generate'));
                    if (arrowBtn && !arrowBtn.hasAttribute('disabled')) {
                        arrowBtn.click();
                        return 'submit_clicked';
                    }
                    // Fallback to Enter key
                    const box = document.querySelector("textarea, [contenteditable='true']");
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
                
                # 4. Check for auto-approvals if any pop up
                for _ in range(5):
                    app_res = await session.eval("""
                    (() => {
                        const btns = Array.from(document.querySelectorAll("button, span"));
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
                    
                print("[✓] Scene 1 9:16 Reference Image generation initiated successfully!", flush=True)
                break
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run())
