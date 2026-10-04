import asyncio
import json
from direct_cdp import DirectCDPClient, get_browser_ws

async def test_input():
    ws_url = await get_browser_ws()
    client = DirectCDPClient(ws_url)
    await client.connect()
    try:
        targets = await client.get_targets()
        flow_target = next(t for t in targets if "flow.google.com/u/2" in t.get("url", ""))
        session = await client.attach_to_target(flow_target["targetId"])
        
        box_info = await session.eval("""
        (() => {
            const pms = Array.from(document.querySelectorAll('div.ProseMirror, [contenteditable="true"]'));
            return pms.map((p, idx) => ({
                idx,
                tag: p.tagName,
                cls: p.className,
                placeholder: p.getAttribute('data-placeholder'),
                text: p.innerText,
                visible: p.offsetWidth > 0 && p.offsetHeight > 0
            }));
        })()
        """)
        print("ProseMirror boxes:", json.dumps(box_info, indent=2))
        
        send_btn_info = await session.eval("""
        (() => {
            const btns = Array.from(document.querySelectorAll("button")).filter(b => {
                const text = b.innerText || '';
                const label = b.getAttribute('aria-label') || '';
                return text.includes('arrow_forward') || label.includes('send') || label.includes('Generate') || label.includes('Start');
            });
            return btns.map(b => ({
                text: b.innerText,
                label: b.getAttribute('aria-label'),
                disabled: b.disabled,
                visible: b.offsetWidth > 0 && b.offsetHeight > 0
            }));
        })()
        """)
        print("Send buttons:", json.dumps(send_btn_info, indent=2))
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_input())
