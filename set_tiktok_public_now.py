import asyncio
from direct_cdp import DirectCDPClient, get_browser_ws

async def set_public():
    ws = await get_browser_ws()
    client = DirectCDPClient(ws)
    await client.connect()
    try:
        targets = await client.get_targets()
        session = None
        for t in targets:
            if t.get("type") == "page" and "tiktok" in t.get("url", ""):
                session = await client.attach_to_target(t["targetId"])
                break
                
        if not session:
            print("TikTok session not found!")
            return
            
        # Refresh to get latest review status
        await session.eval("window.location.reload()")
        await asyncio.sleep(5)
        
        # Check current status of topmost video row
        row_status = await session.eval("""
        (() => {
            const rows = document.querySelectorAll("tbody tr, div[class*='post-list-item'], div[class*='row']");
            const privBtn = Array.from(document.querySelectorAll("button, div[role='button']"))
                .find(b => b.innerText && b.innerText.trim().startsWith('Private'));
            return {
                hasPrivateBtn: !!privBtn,
                btnText: privBtn ? privBtn.innerText.trim() : null
            };
        })()
        """)
        print("Row status:", row_status)
        
        if row_status.get("hasPrivateBtn"):
            # Click private dropdown
            await session.eval("""
            (() => {
                const privBtn = Array.from(document.querySelectorAll("button, div[role='button']"))
                    .find(b => b.innerText && b.innerText.trim().startsWith('Private'));
                if (privBtn) privBtn.click();
            })()
            """)
            await asyncio.sleep(1)
            
            # Click Public option
            click_pub = await session.eval("""
            (() => {
                const items = Array.from(document.querySelectorAll("li, div[role='option'], div[class*='menu-item'], span"));
                const pub = items.find(i => i.innerText && i.innerText.trim().toLowerCase() === 'public');
                if (pub) {
                    pub.click();
                    return 'clicked_public';
                }
                return 'public_option_not_found';
            })()
            """)
            print("Clicked public result:", click_pub)
            await asyncio.sleep(2)
            
        proof_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\tiktok_final_public_proof.png"
        await session.screenshot(proof_path)
        print("Final proof saved to:", proof_path)
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(set_public())
