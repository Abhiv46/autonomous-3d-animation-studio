import asyncio
import sys
from direct_cdp import DirectCDPClient, get_browser_ws

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

async def check():
    ws = await get_browser_ws()
    client = DirectCDPClient(ws)
    await client.connect()
    targets = await client.get_targets()
    for t in targets:
        if 'studio.youtube' in t.get('url', ''):
            session = await client.attach_to_target(t['targetId'])
            url = await session.eval("window.location.href")
            if "video/X-hLtA9-VtM/edit" not in url:
                await session.eval("window.location.href = 'https://studio.youtube.com/video/X-hLtA9-VtM/edit'")
                await asyncio.sleep(4)
                
            data = await session.eval("""
            (() => {
                const title = document.querySelector("#textbox[aria-label*='title' i]");
                const desc = document.querySelector("#textbox[aria-label*='description' i]");
                return {
                    title: title ? title.innerText.trim() : null,
                    descLength: desc ? desc.innerText.trim().length : 0
                };
            })()
            """)
            print("Verified Video Edit State:", data.get("descLength"), "chars in description.")
            proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_verified_fields_proof.png"
            await session.screenshot(proof)
            print("Saved proof to:", proof)
            break
    await client.close()

if __name__ == '__main__':
    asyncio.run(check())
