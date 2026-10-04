import asyncio
import json
from direct_cdp import DirectCDPClient, get_browser_ws

async def check_slots():
    ws_url = await get_browser_ws()
    client = DirectCDPClient(ws_url)
    await client.connect()
    try:
        # Create a new tab to test slots without disturbing existing tabs
        tab_id = await client.create_target("about:blank")
        session = await client.attach_to_target(tab_id)
        
        accounts_status = []
        for slot in range(8):
            url = f"https://flow.google.com/u/{slot}/"
            print(f"Testing slot {slot}: {url}...", flush=True)
            await session.eval(f"window.location.href = '{url}'")
            await asyncio.sleep(4)
            
            info = await session.eval("""
            (() => {
                const currentUrl = window.location.href;
                const title = document.title;
                const emailEl = document.querySelector("[aria-label*='@gmail.com' i], [aria-label*='Google Account' i]");
                const email = emailEl ? emailEl.getAttribute('aria-label') : null;
                const bodyText = document.body ? document.body.innerText : '';
                const hasCreditsBanner = bodyText.includes('credits') || bodyText.includes('credit limit');
                const projectCards = Array.from(document.querySelectorAll("a[href*='/project/']")).map(a => a.href);
                return {
                    slot: window.location.pathname,
                    currentUrl,
                    title,
                    email,
                    hasCreditsBanner,
                    projectCards: projectCards.slice(0, 3)
                };
            })()
            """)
            print(f"Slot {slot} info:", json.dumps(info, indent=2))
            accounts_status.append(info)
            
        await client.send("Target.closeTarget", {"targetId": tab_id})
        with open(r"C:\TheNaughtyDuo_Automation\flow_slots_status.json", "w") as f:
            json.dump(accounts_status, f, indent=2)
        print("Done testing all slots!")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(check_slots())
