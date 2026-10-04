import time
from pathlib import Path
from playwright.sync_api import sync_playwright

VIDEO_FILE = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\TheNaughtyDuo_GoodHabits_Master.mp4")

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    
    btn = page.locator("#select-files-button").first
    print("Found button! Expecting file chooser...")
    
    with page.expect_file_chooser(timeout=15000) as fc_info:
        btn.click()
        
    fc = fc_info.value
    print("File chooser intercepted!")
    print(f"Setting file: {VIDEO_FILE} ({VIDEO_FILE.stat().st_size / (1024*1024):.2f} MB)...")
    fc.set_files(str(VIDEO_FILE))
    print("File set! Waiting 8s for processing...")
    time.sleep(8)
    
    page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\file_upload_progress.png")
    print("Saved screenshot of upload progress!")
