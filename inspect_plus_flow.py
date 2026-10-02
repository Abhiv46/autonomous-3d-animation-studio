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
                
                # Check for '+' button
                plus_info = await session.eval("""
                (() => {
                    const btns = Array.from(document.querySelectorAll("button")).map((b, i) => ({
                        idx: i,
                        text: b.innerText ? b.innerText.trim() : '',
                        aria: b.getAttribute('aria-label') || ''
                    }));
                    return btns.filter(b => b.text === 'add' || b.aria.toLowerCase().includes('add') || b.text.includes('+'));
                })()
                """)
                print("Plus buttons found:", json.dumps(plus_info, ensure_ascii=True))
                
                # Click '+'
                click_res = await session.eval("""
                (() => {
                    const btns = Array.from(document.querySelectorAll("button"));
                    const btn = btns.find(b => b.innerText && b.innerText.trim() === 'add');
                    if (btn) {
                        btn.click();
                        return 'clicked_add';
                    }
                    return 'not_found';
                })()
                """)
                print("Click result:", click_res)
                await asyncio.sleep(2)
                
                # Inspect open elements
                menu_items = await session.eval("""
                (() => {
                    const els = Array.from(document.querySelectorAll("[role='menuitem'], [role='option'], button, span"))
                        .map(el => el.innerText ? el.innerText.trim() : '')
                        .filter(t => t.length > 0 && t.length < 50);
                    return Array.from(new Set(els)).slice(0, 30);
                })()
                """)
                print("Menu items:", json.dumps(menu_items, ensure_ascii=True))
                
                # Dismiss with Escape
                await session.eval("""
                (() => {
                    const esc = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true });
                    document.dispatchEvent(esc);
                })()
                """)
                break
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run())
