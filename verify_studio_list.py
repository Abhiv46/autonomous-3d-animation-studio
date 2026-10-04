import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", wait_until="networkidle")
    time.sleep(3)
    page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\studio_shorts_final_proof.png")
    
    rows = page.evaluate("""() => {
        const trs = Array.from(document.querySelectorAll('ytcp-video-row'));
        return trs.slice(0, 8).map(r => {
            const titleEl = r.querySelector('#video-title');
            const vis = r.querySelector('.cell-body.visibility');
            return {
                title: titleEl ? titleEl.innerText.trim() : '',
                href: titleEl ? titleEl.getAttribute('href') : '',
                vis: vis ? vis.innerText.trim() : ''
            };
        });
    }""")
    for idx, r in enumerate(rows):
        print(f"[{idx}] {r['title'][:50]} | {r['vis']} | {r['href']}")
