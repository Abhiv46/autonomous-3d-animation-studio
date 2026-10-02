import asyncio
import json
from direct_cdp import DirectCDPClient, get_browser_ws

async def run():
    ws_url = await get_browser_ws()
    client = DirectCDPClient(ws_url)
    await client.connect()
    try:
        targets = await client.get_targets()
        for t in targets:
            if t.get("type") == "page" and "flow.google.com" in t.get("url", ""):
                session = await client.attach_to_target(t["targetId"])
                data = await session.eval("""
                (() => {
                    const avatar = document.querySelector("img[src*='googleusercontent'], button[aria-label*='Google Account']");
                    const userBtn = document.querySelector("[aria-label*='@' i]");
                    return {
                        url: window.location.href,
                        ariaLabel: userBtn ? userBtn.getAttribute('aria-label') : (avatar ? avatar.getAttribute('aria-label') : null)
                    };
                })()
                """)
                print("Active Account Info:", json.dumps(data, indent=2))
                break
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run())
