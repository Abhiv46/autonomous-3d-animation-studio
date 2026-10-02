import asyncio
import json
import os
from direct_cdp import DirectCDPClient, get_browser_ws

VIDEO_PATH = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\processed_episodes\TheNaughtyDuo_EP21_MummyKiHighHeels_OriginalAudio_Master.mp4"
TIKTOK_CAPTION = "Kaavya ne pehni Mummy ki high heels! 😂👠 Sassy fashion model Kaavya ko bhaiyya ne pakad liya! Wait for her super cute reaction at the end! 🥰❤️ #TheNaughtyDuo #shorts #viral #funny #comedy #3danimation #hindicartoon #foryou #fyp #trending"

async def main():
    ws_url = await get_browser_ws()
    print("[1] Connecting to browser WS...", flush=True)
    client = DirectCDPClient(ws_url)
    await client.connect()
    
    try:
        targets = await client.get_targets()
        tt_target = None
        for t in targets:
            if t.get("type") == "page" and "tiktok.com" in t.get("url", ""):
                tt_target = t
                break
                
        if not tt_target:
            print("[!] TikTok target not found!")
            return
            
        print(f"[2] Attaching to TikTok target: {tt_target['targetId']}", flush=True)
        session = await client.attach_to_target(tt_target["targetId"])
        
        # Wait 5 seconds for page load
        await asyncio.sleep(5)
        
        # Screenshot
        await session.screenshot(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\tiktok_initial_state.png")
        
        # Check title and URL
        title = await session.eval("document.title")
        url = await session.eval("window.location.href")
        print(f"[3] TikTok URL: {url} | Title: {title}", flush=True)
        
        # Inspect for file input
        info = await session.eval("""
        (() => {
            const inputs = Array.from(document.querySelectorAll("input[type='file']")).map(i => ({
                accept: i.accept,
                visible: i.offsetParent !== null,
                className: i.className
            }));
            const iframes = Array.from(document.querySelectorAll("iframe")).map(f => ({
                src: f.src,
                className: f.className
            }));
            const btns = Array.from(document.querySelectorAll("button")).map(b => b.innerText).filter(t => t && t.trim().length > 0);
            return {
                inputs,
                iframes,
                btns: btns.slice(0, 15)
            };
        })()
        """)
        print("[4] Page inspection:", json.dumps(info, indent=2), flush=True)
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
