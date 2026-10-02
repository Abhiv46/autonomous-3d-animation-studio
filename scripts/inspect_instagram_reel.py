import os
import sys
import json
import re
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

INSTA_URL = "https://www.instagram.com/reel/Dd4K6bCMu0D/"
BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

def inspect_reel():
    res = {}
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 900})

        try:
            page.goto(INSTA_URL, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(6000)

            # Screenshot view
            page.screenshot(path="data/insta_reel_view.png")

            # Extract meta tags
            meta_og_desc = page.locator("meta[property='og:description']").get_attribute("content") or ""
            meta_og_title = page.locator("meta[property='og:title']").get_attribute("content") or ""
            meta_desc = page.locator("meta[name='description']").get_attribute("content") or ""

            res["og_title"] = meta_og_title
            res["og_desc"] = meta_og_desc
            res["meta_desc"] = meta_desc

            # Visible body text
            body_text = page.locator("body").inner_text()
            res["body_text"] = body_text[:2000]

            # Try to grab video tag src
            video_el = page.locator("video").first
            if video_el.count() > 0:
                res["video_src"] = video_el.get_attribute("src")

            # Try to grab reel poster/image
            img_el = page.locator("video").first
            poster = video_el.get_attribute("poster") if video_el.count() > 0 else ""
            res["poster"] = poster

            # Check like / comment / play elements
            likes_el = page.locator("[aria-label*='like' i], span:has-text('likes'), span:has-text('like')").all_inner_texts()
            res["likes_elements"] = likes_el

        except Exception as e:
            res["error"] = str(e)

        browser.close()

    with open("data/insta_reel_data.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    inspect_reel()
