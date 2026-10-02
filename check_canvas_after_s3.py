import asyncio
import json
import urllib.request
from pathlib import Path
from direct_cdp import DirectCDPClient, get_browser_ws

RAW_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips")
RAW_DIR.mkdir(parents=True, exist_ok=True)

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
                
                # Check cards on canvas
                state = await session.eval("""
                (() => {
                    const cards = Array.from(document.querySelectorAll("[class*='tile'], [class*='card'], [role='button']"))
                        .map(el => el.innerText.trim())
                        .filter(t => t.length > 0 && t.length < 60);
                    return Array.from(new Set(cards)).slice(0, 10);
                })()
                """)
                print("Canvas cards now:", state)
                break
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run())
