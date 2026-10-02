import asyncio
from direct_cdp import DirectCDPClient, get_browser_ws

async def run():
    ws_url = await get_browser_ws()
    client = DirectCDPClient(ws_url)
    await client.connect()
    targets = await client.get_targets()
    for t in targets:
        if t.get('type') == 'page' and 'tiktok.com' in t.get('url', ''):
            session = await client.attach_to_target(t['targetId'])
            # Reload page to refresh review status
            await session.eval("window.location.reload()")
            await asyncio.sleep(4)
            await session.screenshot(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\tiktok_final_refreshed.png")
            print("Refreshed TikTok feed!")
            break
    await client.close()

if __name__ == "__main__":
    asyncio.run(run())
