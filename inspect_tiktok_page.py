import asyncio
import json
from direct_cdp import DirectCDPClient, get_browser_ws

async def diag():
    ws = await get_browser_ws()
    client = DirectCDPClient(ws)
    await client.connect()
    targets = await client.get_targets()
    for t in targets:
        if t.get('type') == 'page' and 'tiktok' in t.get('url', ''):
            session = await client.attach_to_target(t['targetId'])
            url = await session.eval('window.location.href')
            print('Found TikTok page:', url)
            
            # Check frames
            frames_res = await session.eval("""
            (() => {
                const iframes = Array.from(document.querySelectorAll('iframe')).map(f => f.src);
                const buttons = Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim());
                const inputs = Array.from(document.querySelectorAll('input')).map(i => ({type: i.type, name: i.name}));
                return {
                    iframes: iframes,
                    buttons: buttons,
                    inputs: inputs
                };
            })()
            """)
            print('Page content:', json.dumps(frames_res, indent=2))
            
            screenshot = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\tiktok_diag.png"
            await session.screenshot(screenshot)
            print("Saved screenshot to:", screenshot)
            break
    await client.close()

if __name__ == '__main__':
    asyncio.run(diag())
