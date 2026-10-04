import sys
import time
import re
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.wait_for_load_state("domcontentloaded")
    time.sleep(2)
    
    rows_data = page.evaluate("""() => {
        const rows = Array.from(document.querySelectorAll('ytcp-video-row'));
        return rows.slice(0, 10).map(r => {
            const titleEl = r.querySelector('#video-title');
            const href = titleEl ? titleEl.getAttribute('href') : '';
            const text = titleEl ? titleEl.innerText.trim() : '';
            return { text, href };
        });
    }""")
    for idx, r in enumerate(rows_data):
        print(f"[{idx}] {r['text'][:40]} | href: {r['href']}")
