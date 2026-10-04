import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    flow_page = next(pg for pg in browser.contexts[0].pages if "flow.google.com" in pg.url)
    flow_page.bring_to_front()
    
    # Click mode badge
    for b in flow_page.locator("button").all():
        txt = b.inner_text().strip()
        if "banana" in txt.lower() or "image" in txt.lower() or "veo" in txt.lower():
            print("Clicking mode badge...")
            b.click()
            time.sleep(1)
            break
            
    flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\mode_popover_debug.png")
    
    # Inspect all elements in overlay
    overlay = flow_page.locator(".cdk-overlay-pane").first
    print("Overlay is visible:", overlay.is_visible())
    for i, el in enumerate(overlay.locator("button, mat-button-toggle, [role='button'], div, span").all()):
        try:
            t = el.inner_text().strip()
            if t in ["Image", "Video", "Frames", "Ingredients", "9:16", "16:9"] or "veo" in t.lower():
                print(f"[{i}] {t}: box={el.bounding_box()}")
        except Exception:
            pass
