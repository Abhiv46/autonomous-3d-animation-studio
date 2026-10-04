import time
from playwright.sync_api import sync_playwright

video_path = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\TheNaughtyDuo_GoodHabits_Master.mp4"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    
    # Locate file input in upload dialog
    picker_input = page.locator("ytcp-uploads-file-picker input[type='file']")
    print("Found picker input:", picker_input.count())
    
    if picker_input.count() > 0:
        picker_input.first.set_input_files(video_path)
        print("Set input files successfully!")
        time.sleep(6)
        
    page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\after_direct_set.png")
    print("Saved screenshot after direct set!")
