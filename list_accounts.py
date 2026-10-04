import asyncio
from direct_cdp import DirectCDPClient, get_browser_ws

async def list_accounts():
    ws = await get_browser_ws()
    client = DirectCDPClient(ws)
    await client.connect()
    targets = await client.get_targets()
    for t in targets:
        if 'accounts.google' in t.get('url', ''):
            session = await client.attach_to_target(t['targetId'])
            accs = await session.eval("""
            (() => {
                const list = Array.from(document.querySelectorAll("li, div[data-identifier], div[role='link']"));
                return list.map(e => (e.innerText || '').trim().replace(/\\n/g, ' - ')).filter(t => t.includes('@'));
            })()
            """)
            print('Accounts in chooser:')
            if accs:
                for a in set(accs):
                    print(' ', a)
            break
    await client.close()

if __name__ == '__main__':
    asyncio.run(list_accounts())
