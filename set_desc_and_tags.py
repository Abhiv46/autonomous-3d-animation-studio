import asyncio
import json
import base64
import urllib.request
import websockets

VID_ID = "k2JBp96Iqa4"

YT_DESC = """Kaartik aur Kaavya pahunch gaye ek jadui Rainbow World me jahan se saare rang gayab ho gaye! 🌈😱
Lekin kya Kaavya aur Kaartik milkar Laal Seb, Neeli Titli, Peela Suraj aur Saare Colors wapas laa payenge? 🍎🦋☀️🌱

Dekhiye unka sabse pyara aur mazedaar Magic Color Adventure! 🥰✨

💬 Sawaal: Aapka sabse favourite color kaunsa hai? Comment me batayein! 👇❤️💙💛💚

🔔 Aise hi mazedaar aur cute 3D family cartoon stories ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! ✨

#TheNaughtyDuo #shorts #viral #funny #colorsong #rainbow #3danimation #hindicartoon #kidsanimation #cartoons #trending #ytshorts #learningcolors #funnycartoon #family"""

YT_TAGS = [
    "The Naughty Duo", "TheNaughtyDuo", "Kaartik and Kaavya", "learn colors hindi",
    "color song", "rainbow cartoon", "3d animation hindi", "hindi cartoon funny",
    "kids animation", "nursery rhyme hindi", "cartoon for toddlers", "relatable comedy",
    "shorts", "viral shorts", "trending shorts"
]

async def set_desc():
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read())
    yt_tab = next(t for t in tabs if "studio.youtube.com" in t.get("url", "").lower())
    ws_url = yt_tab["webSocketDebuggerUrl"]
    async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
        msg_id = 0
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cid = msg_id
            await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get("id") == cid: return resp.get("result", {})

        # Navigate to edit page
        await call("Page.navigate", {"url": f"https://studio.youtube.com/video/{VID_ID}/edit"})
        await asyncio.sleep(4)

        # Fill description
        await call("Runtime.evaluate", {
            "expression": f"""
            (() => {{
                const descBox = document.querySelector("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox");
                if (descBox) {{
                    descBox.focus();
                    document.execCommand('selectAll', false, null);
                    document.execCommand('delete', false, null);
                    document.execCommand('insertText', false, {json.dumps(YT_DESC)});
                    descBox.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    return 'filled';
                }}
                return 'no_box';
            }})()
            """,
            "returnByValue": True,
            "awaitPromise": True
        })
        await asyncio.sleep(1)

        # Click show more
        await call("Runtime.evaluate", {
            "expression": """
            (() => {
                const btn = document.querySelector('#toggle-button, ytcp-button:has-text("Show more")');
                if (btn) btn.click();
            })()
            """
        })
        await asyncio.sleep(1)

        # Fill tags
        tags_string = ", ".join(YT_TAGS) + ","
        await call("Runtime.evaluate", {
            "expression": f"""
            (() => {{
                const tagsInput = document.querySelector("input[aria-label*='Tag' i], input[placeholder*='tag' i], #tags-container input");
                if (tagsInput) {{
                    tagsInput.focus();
                    document.execCommand('insertText', false, {json.dumps(tags_string)});
                    tagsInput.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', keyCode: 13, bubbles: true }}));
                    return 'tags_filled';
                }}
                return 'no_tags';
            }})()
            """,
            "returnByValue": True,
            "awaitPromise": True
        })
        await asyncio.sleep(1)

        # Click Save
        res = await call("Runtime.evaluate", {
            "expression": """
            (() => {
                const btn = document.querySelector('button#save, ytcp-button#save-button');
                if (btn && !btn.disabled) {
                    btn.click();
                    return 'saved';
                }
                return 'disabled_or_none';
            })()
            """,
            "returnByValue": True,
            "awaitPromise": True
        })
        print("Save button result:", res.get("result", {}).get("value"))
        await asyncio.sleep(3)

        # Take screenshot of edit page
        await call("Page.enable")
        s_res = await call("Page.captureScreenshot", {"format": "png"})
        proof = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\yt_color_edit_fully_saved.png"
        with open(proof, "wb") as f:
            f.write(base64.b64decode(s_res["data"]))
        print("Saved proof to", proof)

if __name__ == "__main__":
    asyncio.run(set_desc())
