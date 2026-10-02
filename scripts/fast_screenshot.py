import base64
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    cdp_session = page.context.new_cdp_session(page)
    res = cdp_session.send("Page.captureScreenshot")
    with open(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\fast_cdp_screen.png", "wb") as f:
        f.write(base64.b64decode(res["data"]))
    print("Fast CDP screenshot captured!")
