from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Check top left tile (the new card)
    top_left = page.locator("text='kaavya Semi-realistic'").first
    if top_left.count() > 0:
        parent = top_left.locator("..")
        print("Top left tile text:", parent.inner_text().strip())

    # Check toast, snackbar or warning
    toasts = page.locator("mat-snack-bar-container, .cdk-overlay-pane, [role='alert']").all()
    print("Alerts count:", len(toasts))
    for t in toasts:
        try:
            print("Alert text:", t.inner_text().strip())
        except Exception:
            pass

    # Check the orange button
    all_btns = page.locator("button").all()
    for b in all_btns:
        try:
            txt = b.inner_text().strip()
            aria = b.get_attribute("aria-label") or ""
            if "info" in txt.lower() or "warn" in (b.get_attribute("class") or "").lower():
                print(f"Info button: text='{txt}', aria='{aria}'")
                # Hover to see tooltip
                b.hover()
                page.wait_for_timeout(1000)
                tooltips = page.locator("mat-tooltip-component, [role='tooltip']").all()
                for tt in tooltips:
                    print("Tooltip:", tt.inner_text().strip())
        except Exception:
            pass
