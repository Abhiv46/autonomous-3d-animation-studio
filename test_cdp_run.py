import asyncio
from direct_cdp import DirectCDPClient, get_browser_ws

async def main():
    ws_url = await get_browser_ws()
    print("Connecting to:", ws_url, flush=True)
    client = DirectCDPClient(ws_url)
    await client.connect()
    try:
        targets = await client.get_targets()
        print(f"Found {len(targets)} targets:", flush=True)
        yt_target = None
        for t in targets:
            print(f"  Target [{t['type']}]: {t.get('title')} ({t.get('url')[:60]}...)", flush=True)
            if "youtube" in t.get("url", ""):
                yt_target = t
                
        if yt_target:
            print("Attaching to YouTube target...", flush=True)
            session = await client.attach_to_target(yt_target["targetId"])
            title = await session.eval("document.title")
            print("Successfully evaluated title:", title, flush=True)
            await session.screenshot(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_live_direct_cdp.png")
            print("Screenshot saved successfully!", flush=True)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
