import asyncio
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
                
                # Click The Naughty Duo project
                click_res = await session.eval("""
                (() => {
                    const cards = Array.from(document.querySelectorAll("div, a, button, [role='button']"));
                    const projectCard = cards.find(c => c.innerText && c.innerText.includes("The Naughty Duo"));
                    if (projectCard) {
                        projectCard.click();
                        return 'project_clicked';
                    }
                    return 'project_not_found';
                })()
                """)
                print("Click result:", click_res)
                await asyncio.sleep(6)
                
                url = await session.eval("window.location.href")
                title = await session.eval("document.title")
                print(f"Canvas URL: {url} | Title: {title}")
                await session.screenshot(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\project_canvas_live.png")
                break
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run())
