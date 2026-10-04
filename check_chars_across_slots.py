import asyncio
import json
from direct_cdp import DirectCDPClient, get_browser_ws

async def check_chars():
    ws_url = await get_browser_ws()
    client = DirectCDPClient(ws_url)
    await client.connect()
    try:
        tab_id = await client.create_target("about:blank")
        session = await client.attach_to_target(tab_id)
        
        test_urls = [
            ("slot_0", "https://flow.google.com/u/0/project/a1c6f19b-b046-41f3-9b33-fbc756646163"),
            ("slot_1", "https://flow.google.com/u/1/project/b9bdf8ac-1466-46fe-ad69-30148b5b93fa"),
            ("slot_2", "https://flow.google.com/u/2/project/1fc9b4e8-54eb-4141-907d-77002b691fc7"),
            ("slot_3", "https://flow.google.com/u/3/project/1fc877d7-73dd-4627-b635-df6b3549ee9e")
        ]
        
        for name, url in test_urls:
            await session.eval(f"window.location.href = '{url}'")
            await asyncio.sleep(4)
            info = await session.eval("""
            (() => {
                const title = document.title;
                const body = document.body ? document.body.innerText : '';
                const hasKaartik = body.includes('Kaartik') || body.includes('Kaavya');
                const imgs = Array.from(document.querySelectorAll('img')).map(i => i.src).filter(s => s && !s.includes('svg'));
                return { title, hasKaartik, imgCount: imgs.length };
            })()
            """)
            print(f"[{name}] {url} -> {info}")
            
        await client.send("Target.closeTarget", {"targetId": tab_id})
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(check_chars())
