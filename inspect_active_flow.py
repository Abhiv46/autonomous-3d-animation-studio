import asyncio
import json
import base64
from direct_cdp import DirectCDPClient, get_browser_ws

async def inspect():
    ws_url = await get_browser_ws()
    client = DirectCDPClient(ws_url)
    await client.connect()
    try:
        targets = await client.get_targets()
        flow_target = next(t for t in targets if "flow.google.com" in t.get("url", ""))
        session = await client.attach_to_target(flow_target["targetId"])
        
        info = await session.eval("""
        (() => {
            const url = window.location.href;
            const pm = document.querySelector('div.ProseMirror');
            const btns = Array.from(document.querySelectorAll('button')).map(b => b.innerText ? b.innerText.trim() : '').filter(Boolean);
            const pills = Array.from(document.querySelectorAll('.pill, [role="tab"], .tag, flow-pill')).map(p => p.innerText.trim()).filter(Boolean);
            const images = Array.from(document.querySelectorAll('img')).map(i => i.src).filter(s => s && !s.includes('data:image/svg'));
            return {
                url,
                hasPm: !!pm,
                pmText: pm ? pm.innerText : '',
                btns: btns.slice(0, 35),
                pills: pills.slice(0, 20),
                imagesCount: images.length
            };
        })()
        """)
        print("Flow Page Info:", json.dumps(info, indent=2))
        
        # Take screenshot
        res = await session.send("Page.captureScreenshot", {"format": "png"})
        proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\flow_current_state.png"
        with open(proof, "wb") as f:
            f.write(base64.b64decode(res["data"]))
        print(f"Screenshot saved to {proof}!")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(inspect())
