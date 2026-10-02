import asyncio
import json
from direct_cdp import DirectCDPClient, get_browser_ws

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
                
                # 1. Click the mode button at the bottom of prompt bar
                print("[2] Clicking mode button...", flush=True)
                res = await session.eval("""
                (() => {
                    const btns = Array.from(document.querySelectorAll("button"));
                    const modeBtn = btns.find(b => b.innerText && (b.innerText.includes('Video') || b.innerText.includes('720p')));
                    if (modeBtn) {
                        modeBtn.click();
                        return 'mode_clicked';
                    }
                    return 'mode_not_found';
                })()
                """)
                print(f"    Mode click: {res}", flush=True)
                await asyncio.sleep(2)
                
                # 2. Inspect all elements in open menu/popover
                options = await session.eval("""
                (() => {
                    const els = Array.from(document.querySelectorAll("[role='tab'], [role='menuitem'], [role='option'], button, span"))
                        .map(el => ({ tag: el.tagName, text: el.innerText ? el.innerText.trim() : '', role: el.getAttribute('role') }))
                        .filter(x => x.text && x.text.length > 0 && x.text.length < 40);
                    return els.slice(0, 30);
                })()
                """)
                print("Open popover items:", json.dumps(options, indent=2), flush=True)
                
                # 3. Check if 'Image' is an option and click it
                click_img = await session.eval("""
                (() => {
                    const candidates = Array.from(document.querySelectorAll("button, [role='tab'], [role='option'], span"));
                    const imgTab = candidates.find(c => c.innerText && c.innerText.trim() === 'Image');
                    if (imgTab) {
                        imgTab.click();
                        return 'image_tab_clicked';
                    }
                    return 'image_tab_not_found';
                })()
                """)
                print(f"    Image tab click: {click_img}", flush=True)
                await asyncio.sleep(2)
                
                # Screenshot of image mode
                await session.screenshot(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\flow_image_mode_active.png")
                print("[✓] Screenshot saved: flow_image_mode_active.png", flush=True)
                break
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run())
