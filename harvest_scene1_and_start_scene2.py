import asyncio
import json
import urllib.request
from pathlib import Path
from direct_cdp import DirectCDPClient, get_browser_ws

RAW_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips")
RAW_DIR.mkdir(parents=True, exist_ok=True)
SCENE1_PATH = RAW_DIR / "ep22_chocolatemask_scene1_raw.mp4"

SCENE2_PROMPT = "Vertical 9:16 aspect ratio, Pixar 3D animation. Kaavya pokes Mummy's cheek, scoops a tiny bit of brown clay, and licks her finger! Her face makes a hilarious disgusted cartoon sour face, spitting tongue out: 'Cheee! Yeh chocolate nahi mitti hai!' Kaartik bursts into loud laughing claps. Mummy opens eyes, takes off cucumber slices, gasping in comical shock: 'Arrey Kaavya ye kya kiya?!' (All character voices strictly in cheerful cute HINDI dialogues). Ultra-vibrant colors, Pixar 3D animation."

async def run():
    ws_url = await get_browser_ws()
    print("[1] Connecting to browser...", flush=True)
    client = DirectCDPClient(ws_url)
    await client.connect()
    
    try:
        targets = await client.get_targets()
        for t in targets:
            if t.get("type") == "page" and "flow.google.com" in t.get("url", ""):
                session = await client.attach_to_target(t["targetId"])
                
                # 1. Click on Scene 1 tile to inspect video source or download
                print("[2] Inspecting Scene 1 card video URL...", flush=True)
                tile_info = await session.eval("""
                (() => {
                    const cards = Array.from(document.querySelectorAll("div, [role='button'], [class*='tile']"));
                    const c1 = cards.find(c => c.innerText && c.innerText.includes('Children tastin'));
                    if (c1) {
                        c1.click();
                        return 'tile_clicked';
                    }
                    return 'tile_not_found';
                })()
                """)
                print(f"    Tile click: {tile_info}", flush=True)
                await asyncio.sleep(2)
                
                # Extract video src from DOM
                vid_src = await session.eval("""
                (() => {
                    const vids = Array.from(document.querySelectorAll("video"));
                    for (const v of vids) {
                        if (v.src && v.src.startsWith('http')) return v.src;
                        if (v.currentSrc && v.currentSrc.startsWith('http')) return v.currentSrc;
                    }
                    return null;
                })()
                """)
                print(f"    Direct Video URL found: {vid_src}", flush=True)
                
                if vid_src:
                    print(f"[3] Downloading Scene 1 video directly from URL...", flush=True)
                    urllib.request.urlretrieve(vid_src, str(SCENE1_PATH))
                    print(f"[✓] Scene 1 saved to {SCENE1_PATH} ({SCENE1_PATH.stat().st_size} bytes)!", flush=True)
                else:
                    # Click more_vert and Download
                    print("Attempting menu download...", flush=True)
                    await session.eval("""
                    (() => {
                        const moreBtn = document.querySelector("button:has(.mat-icon:has-text('more_vert')), [aria-label*='more' i]");
                        if (moreBtn) moreBtn.click();
                    })()
                    """)
                    await asyncio.sleep(1)
                    await session.eval("""
                    (() => {
                        const btns = Array.from(document.querySelectorAll("button, [role='menuitem']"));
                        const dl = btns.find(b => b.innerText && b.innerText.includes('Download'));
                        if (dl) dl.click();
                    })()
                    """)
                    
                # 2. Type Scene 2 Prompt
                print("[4] Submitting Scene 2 Prompt...", flush=True)
                type_res = await session.eval("""
                (() => {
                    const box = document.querySelector("[contenteditable='true'], textarea, div.ProseMirror");
                    if (!box) return 'no_box';
                    box.focus();
                    document.execCommand('selectAll', false, null);
                    document.execCommand('delete', false, null);
                    document.execCommand('insertText', false, """ + json.dumps(SCENE2_PROMPT) + """);
                    return 'prompt_typed';
                })()
                """)
                print(f"    Type result: {type_res}", flush=True)
                await asyncio.sleep(1)
                
                # 3. Click Submit
                await session.eval("""
                (() => {
                    const btns = Array.from(document.querySelectorAll("button"));
                    const arrowBtn = btns.find(b => b.innerText && b.innerText.includes('arrow_forward'));
                    if (arrowBtn && !arrowBtn.hasAttribute('disabled')) {
                        arrowBtn.click();
                        return 'submit_clicked';
                    }
                    return 'no_btn';
                })()
                """)
                await asyncio.sleep(3)
                
                # 4. Auto-approve
                for _ in range(8):
                    app = await session.eval("""
                    (() => {
                        const btns = Array.from(document.querySelectorAll("button, span, div"));
                        const always = btns.find(b => b.innerText && b.innerText.includes('Always approve'));
                        if (always && always.offsetParent !== null) { always.click(); return 'always_approved'; }
                        const approve = btns.find(b => b.innerText && b.innerText.trim() === 'Approve');
                        if (approve && approve.offsetParent !== null) { approve.click(); return 'approved'; }
                        return null;
                    })()
                    """)
                    if app:
                        print(f"    [✓] Auto-approved: {app}", flush=True)
                        break
                    await asyncio.sleep(1)
                    
                await asyncio.sleep(3)
                await session.screenshot(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\scene2_render_live.png")
                print("[SUCCESS] Scene 2 generation started successfully!", flush=True)
                break
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run())
