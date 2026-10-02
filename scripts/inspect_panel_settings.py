import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Inspect all buttons at the bottom of the right panel
    chat_container = page.locator(".chat-container, [role='region'], aside, .right-panel").first
    btns = page.locator("button").all()
    print("Found total buttons:", len(btns))
    for b in btns:
        try:
            if b.is_visible():
                aria = b.get_attribute("aria-label") or ""
                txt = b.inner_text().strip()
                cls = b.get_attribute("class") or ""
                if any(w in (aria + txt + cls).lower() for w in ["setting", "tune", "aspect", "ratio", "image", "video", "send", "generate", "add"]):
                    print(f"Panel button: aria='{aria}', text='{txt}', class='{cls}'")
        except Exception:
            pass
