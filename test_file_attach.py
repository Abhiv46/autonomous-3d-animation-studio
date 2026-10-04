from playwright.sync_api import sync_playwright
import time
from pathlib import Path

VIDEO_FILE = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\TheNaughtyDuo_GoodHabits_Master.mp4")

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    
    # In YouTube Studio, the file input is inside ytcp-uploads-file-picker:
    # <input type="file" class="style-scope ytcp-uploads-file-picker" accept="video/*" ...>
    # In shadow DOM! Let's check shadow DOM or file chooser:
    btn = page.locator("#select-files-button").first
    print("Select files button found:", btn.count())
    
    with page.expect_file_chooser(timeout=10000) as fc_info:
        btn.click()
        
    fc = fc_info.value
    print("File chooser intercepted! Setting files...")
    fc.set_files(str(VIDEO_FILE))
    print("File set! Waiting 5s...")
    time.sleep(5)
    
    page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\after_file_set.png")
    print("Screenshot saved!")
