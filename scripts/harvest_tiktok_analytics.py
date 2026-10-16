import os
import sys
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from browser.engine.pinned_brave import DEFAULT_CDP_ENDPOINT, ensure_pinned_brave

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

OUT_FILE = BASE_DIR / "data" / "tiktok_studio_analytics_harvest.json"
SCR_PATH = BASE_DIR / "data" / "tiktok_content_page_full.png"

def harvest_tiktok_posts():
    print("[*] Launching Brave to audit TikTok Studio Content...", flush=True)
    ensure_pinned_brave()
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(os.getenv("FLOW_CDP_ENDPOINT", DEFAULT_CDP_ENDPOINT))
        context = browser.contexts[0]
        page = context.new_page()
        try:
            page.set_viewport_size({"width": 1600, "height": 1000})
            page.goto("https://www.tiktok.com/tiktokstudio/content", wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(6000)
            page.screenshot(path=str(SCR_PATH), full_page=True)
            print(f"[+] Saved content list screenshot to: {SCR_PATH}", flush=True)

            rows = page.locator("tbody tr, [role='row']")
            print(f"[*] Found {rows.count()} potential structured rows", flush=True)
            text_content = page.locator("body").inner_text()
            post_data = page.evaluate('''() => {
                let rows = Array.from(document.querySelectorAll('tbody tr'));
                if (rows.length === 0) rows = Array.from(document.querySelectorAll('[role="row"]'));
                return rows.map(r => (r.innerText || '').replace(/\\n+/g, ' | ').trim()).filter(t => t.length > 5);
            }''')
            payload = {
                "harvested_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "post_rows": post_data,
                "raw_page_text": text_content[:20000]
            }
            OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
            temporary = OUT_FILE.with_suffix(".json.tmp")
            temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            temporary.replace(OUT_FILE)
            print(f"[✓] Harvested {len(post_data)} structured TikTok rows into {OUT_FILE}", flush=True)
        finally:
            page.close()
            browser.close()

if __name__ == "__main__":
    harvest_tiktok_posts()
