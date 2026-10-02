from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\live_screen_check.png")
    print("URL:", page.url)

    # Check dialogs or errors
    dialogs = page.locator("[role='dialog'], .cdk-overlay-pane, .mat-mdc-dialog-container").all()
    print("Dialogs count:", len(dialogs))
    for d in dialogs:
        try:
            print("Dialog text:", d.inner_text()[:200])
        except Exception:
            pass

    # Check prompt box content
    editor = page.locator(".ProseMirror")
    if editor.count() > 0:
        print("Editor text length:", len(editor.first.inner_text()))
        print("Editor preview:", editor.first.inner_text()[:150])

    # Check generate button status
    gen_btn = page.locator("button[aria-label='Start generation']").first
    if gen_btn.count() > 0:
        print("Generate button visible:", gen_btn.is_visible())
        print("Generate button enabled:", gen_btn.is_enabled())
    else:
        print("Generate button not found with aria-label='Start generation'")

    # Check all buttons with generate or submit
    all_btns = page.locator("button").all()
    for b in all_btns:
        try:
            aria = b.get_attribute("aria-label") or ""
            txt = b.inner_text() or ""
            if "generat" in aria.lower() or "generat" in txt.lower():
                print(f"Gen btn match: aria='{aria}', text='{txt}', enabled={b.is_enabled()}, visible={b.is_visible()}")
        except Exception:
            pass
