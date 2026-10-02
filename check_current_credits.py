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
                
                # Check for account details button
                info = await session.eval("""
                (() => {
                    const accBtn = document.querySelector("[aria-label='Account details'], .header-user-button, [aria-label*='Account' i]");
                    if (accBtn) {
                        accBtn.click();
                        return 'account_btn_clicked';
                    }
                    return 'account_btn_not_found';
                })()
                """)
                print("Click account info:", info)
                await asyncio.sleep(2)
                
                # Extract modal text and credit numbers
                modal_text = await session.eval("""
                (() => {
                    const modal = document.querySelector("[role='dialog'], [class*='dialog'], [class*='overlay'], [class*='popover'], mat-dialog-container");
                    if (modal) {
                        return modal.innerText;
                    }
                    return document.body.innerText.slice(-1000);
                })()
                """)
                print("--- MODAL / CREDITS TEXT ---")
                print(modal_text)
                print("----------------------------")
                await session.screenshot(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\live_credits_check.png")
                break
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run())
