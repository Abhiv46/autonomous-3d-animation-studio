from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Inspect all elements inside the prompt container
    btns = page.locator("button").all()
    print("Total buttons:", len(btns))
    for b in btns:
        try:
            if b.is_visible():
                aria = b.get_attribute("aria-label") or ""
                txt = b.inner_text() or ""
                print(f"Visible Button: aria='{aria}', text='{txt.strip()}'")
        except Exception:
            pass

    # Inspect kaavya tile
    kaavya_el = page.locator("text='kaavya'").first
    if kaavya_el.count() > 0:
        print("[+] 'kaavya' tile visible:", kaavya_el.is_visible())
