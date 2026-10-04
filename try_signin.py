import asyncio
from direct_cdp import DirectCDPClient, get_browser_ws

async def click_signin():
    ws = await get_browser_ws()
    client = DirectCDPClient(ws)
    await client.connect()
    targets = await client.get_targets()
    for t in targets:
        if 'studio.youtube' in t.get('url', ''):
            session = await client.attach_to_target(t['targetId'])
            res = await session.eval("""
            (() => {
                const btn = Array.from(document.querySelectorAll("button, a")).find(b => b.innerText && b.innerText.trim() === 'Sign in');
                if (btn) {
                    btn.click();
                    return 'signin_clicked';
                }
                return 'no_signin_btn';
            })()
            """)
            print('Sign in click:', res)
            await asyncio.sleep(4)
            await session.screenshot(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_after_signin_click.png")
            break
    await client.close()

if __name__ == '__main__':
    asyncio.run(click_signin())
