import asyncio
import json
from direct_cdp import DirectCDPClient, get_browser_ws

async def inspect_projects():
    ws_url = await get_browser_ws()
    client = DirectCDPClient(ws_url)
    await client.connect()
    try:
        tab_id = await client.create_target("about:blank")
        session = await client.attach_to_target(tab_id)
        
        projects = {
            "slot_0": ["https://flow.google.com/u/0/project/55542498-21b6-462b-86ed-fe84daee4324", "https://flow.google.com/u/0/project/a1c6f19b-b046-41f3-9b33-fbc756646163"],
            "slot_1": ["https://flow.google.com/u/1/project/b9bdf8ac-1466-46fe-ad69-30148b5b93fa"],
            "slot_2": ["https://flow.google.com/u/2/project/1fc9b4e8-54eb-4141-907d-77002b691fc7", "https://flow.google.com/u/2/project/28704e19-7200-4c0b-ab84-8e072ef4e201"],
            "slot_3": ["https://flow.google.com/u/3/project/1fc877d7-73dd-4627-b635-df6b3549ee9e", "https://flow.google.com/u/3/project/abaca554-2cdc-4fc1-89fc-420b202d4c62"]
        }
        
        results = {}
        for slot, p_urls in projects.items():
            for url in p_urls:
                await session.eval(f"window.location.href = '{url}'")
                await asyncio.sleep(4)
                info = await session.eval("""
                (() => {
                    const title = document.title;
                    const h1 = document.querySelector('h1')?.innerText || '';
                    const imgs = document.querySelectorAll('img').length;
                    const pm = !!document.querySelector('div.ProseMirror');
                    return { title, h1, imgs, pm, url: window.location.href };
                })()
                """)
                results[url] = info
                print(f"[{slot}] {url} -> {info}")
                
        await client.send("Target.closeTarget", {"targetId": tab_id})
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(inspect_projects())
