import asyncio
from direct_cdp import DirectCDPClient, get_browser_ws

async def run():
    ws_url = await get_browser_ws()
    client = DirectCDPClient(ws_url)
    await client.connect()
    try:
        targets = await client.get_targets()
        page_target = None
        for t in targets:
            if t.get("type") == "page":
                page_target = t
                break
                
        if not page_target:
            print("[!] No page target found!")
            return
            
        print("Attaching to page target:", page_target["targetId"])
        session = await client.attach_to_target(page_target["targetId"])
        print("Navigating to https://flow.google.com/u/1/ ...")
        await session.navigate("https://flow.google.com/u/1/")
        await asyncio.sleep(6)
        
        title = await session.eval("document.title")
        url = await session.eval("window.location.href")
        print(f"Current Page: {url} | Title: {title}")
        
        await session.screenshot(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\flow_slot1_test.png")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run())
