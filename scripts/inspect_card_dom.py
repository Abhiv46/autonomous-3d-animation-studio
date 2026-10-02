from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    links = page.locator("a").all()
    print("Links count:", len(links))
    for l in links:
        try:
            href = l.get_attribute("href") or ""
            txt = l.inner_text() or ""
            print(f"A Link: href='{href}', text='{txt.strip()}'")
        except Exception:
            pass

    images = page.locator("img").all()
    print("Images count:", len(images))
    for idx, img in enumerate(images):
        try:
            src = img.get_attribute("src") or ""
            print(f"Img {idx}: src='{src[:60]}'")
        except Exception:
            pass
