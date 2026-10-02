import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
OUT_FILE = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\tiktok_studio_analytics_harvest.json"
SCR_PATH = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\tiktok_content_page_full.png"

def harvest_tiktok_posts():
    print("[*] Launching Brave to audit TikTok Studio Content...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        page.goto("https://www.tiktok.com/tiktokstudio/content", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(6000)

        # Let's take full screenshot
        page.screenshot(path=SCR_PATH, full_page=True)
        print(f"[+] Saved content list screenshot to: {SCR_PATH}", flush=True)

        # Scrape all visible table rows / cards
        items = []
        rows = page.locator("div[role='row'], div.table-row, tr, div.post-row, div.content-item")
        row_count = rows.count()
        print(f"[*] Found {row_count} potential row elements", flush=True)

        # Fallback: extract all text content from table body
        text_content = page.evaluate('''() => {
            const table = document.querySelector('table') || document.querySelector('[role="table"]') || document.body;
            return table.innerText;
        }''')

        # Also let's extract structured info via JS
        post_data = page.evaluate('''() => {
            const results = [];
            // Try to find each post row
            const rows = document.querySelectorAll('tbody tr') || document.querySelectorAll('[role="row"]');
            rows.forEach(r => {
                const text = r.innerText.replace(/\\n+/g, ' | ');
                if (text.length > 5) {
                    results.push(text);
                }
            });
            return results;
        }''')

        payload = {
            "harvested_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "post_rows": post_data,
            "raw_page_text": text_content[:5000]
        }

        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        print(f"[✓] Harvested {len(post_data)} TikTok post rows into {OUT_FILE}", flush=True)
        browser.close()

if __name__ == "__main__":
    harvest_tiktok_posts()
