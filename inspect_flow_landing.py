import asyncio
from direct_cdp import DirectCDPClient, get_browser_ws

async def run():
    ws_url = await get_browser_ws()
    client = DirectCDPClient(ws_url)
    await client.connect()
    targets = await client.get_targets()
    for t in targets:
        if t.get("type") == "page" and "flow.google.com" in t.get("url", ""):
            session = await client.attach_to_target(t["targetId"])
            js = """
            (() => {
                const textNodes = Array.from(document.querySelectorAll("button, a, div, span, h2, h3"))
                    .map(el => el.innerText ? el.innerText.trim() : "")
                    .filter(t => t.length > 0 && t.length < 50);
                const unique = Array.from(new Set(textNodes));
                return unique.filter(u => 
                    u.toLowerCase().includes("naughty") || 
                    u.toLowerCase().includes("project") || 
                    u.toLowerCase().includes("credit") ||
                    u.toLowerCase().includes("high")
                );
            })()
            """
            projects = await session.eval(js)
            print("Found items on Flow landing:", projects)
            break
    await client.close()

if __name__ == "__main__":
    asyncio.run(run())
