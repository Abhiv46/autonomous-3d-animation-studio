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
                
                # Check options in dropdown
                click_info = await session.eval("""
                (() => {
                    const btns = Array.from(document.querySelectorAll("button"));
                    const modeBtn = btns.find(b => b.innerText && (b.innerText.includes('720p') || b.innerText.includes('Video')));
                    if (modeBtn) {
                        modeBtn.click();
                        return 'mode_clicked';
                    }
                    return 'mode_btn_not_found';
                })()
                """)
                print("Click result:", click_info)
                await asyncio.sleep(1)
                
                # Inspect open popover/menu items
                menu_items = await session.eval("""
                (() => {
                    const items = Array.from(document.querySelectorAll("[role='menuitem'], [role='option'], mat-option, [class*='menu-item'], button"))
                        .map(el => el.innerText.trim())
                        .filter(t => t.length > 0 && t.length < 50);
                    return Array.from(new Set(items));
                })()
                """)
                print("Available menu options:", menu_items[:25])
                await session.screenshot(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\flow_mode_menu.png")
                break
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run())
