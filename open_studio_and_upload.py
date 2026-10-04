import asyncio
from direct_cdp import DirectCDPClient, get_browser_ws

async def open_studio():
    ws = await get_browser_ws()
    client = DirectCDPClient(ws)
    await client.connect()
    targets = await client.get_targets()
    for t in targets:
        if t.get('type') == 'page' and 'youtube.com' in t.get('url', ''):
            session = await client.attach_to_target(t['targetId'])
            print('Navigating to studio.youtube.com...')
            await session.eval("window.location.href = 'https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short'")
            await asyncio.sleep(6)
            url = await session.eval('window.location.href')
            title = await session.eval('document.title')
            print('Studio URL:', url)
            print('Studio Title:', title)
            await session.screenshot(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\studio_live_check.png")
            break
    await client.close()

if __name__ == '__main__':
    asyncio.run(open_studio())
