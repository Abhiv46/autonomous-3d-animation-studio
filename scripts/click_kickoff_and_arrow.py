from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Look for buttons below "costing 15 credits"
    btns = page.locator("button").all()
    print("Total buttons:", len(btns))
    for b in btns:
        try:
            if b.is_visible():
                txt = b.inner_text().strip()
                aria = b.get_attribute("aria-label") or ""
                if any(w in (txt + aria).lower() for w in ["yes", "kick", "confirm", "approve", "generate", "start"]):
                    print(f"Action Button: text='{txt}', aria='{aria}'")
                    # If it's the approve/kickoff button, click it!
                    if any(w in txt.lower() for w in ["yes", "generate", "approve"]):
                        print("Clicking confirmation button...")
                        b.click(force=True)
                        page.wait_for_timeout(2000)
        except Exception:
            pass

    # Also click the white arrow button in the prompt box at the bottom right!
    arrow_btn = page.locator("button.generate-icon-button, button:has-text('arrow_forward')").last
    if arrow_btn.count() > 0 and arrow_btn.is_enabled():
        print("Clicking white arrow button in prompt box...")
        arrow_btn.click(force=True)
        page.wait_for_timeout(2000)
