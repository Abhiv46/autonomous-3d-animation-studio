from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data",
        executable_path=r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto("https://www.tiktok.com/tiktokstudio/content", wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(6000)
    
    dropdown_btn = page.locator("[data-e2e='privacy-select'], button:has-text('Private')").first
    if dropdown_btn.count() > 0 and dropdown_btn.is_visible():
        print("[+] Found Private dropdown, setting to Public...")
        dropdown_btn.click(force=True)
        page.wait_for_timeout(1500)
        public_opt = page.locator("li:has-text('Public'), div:has-text('Public'), [role='option']:has-text('Public')").first
        if public_opt.count() > 0 and public_opt.is_visible():
            public_opt.click(force=True)
            page.wait_for_timeout(2000)
            print("[+] Changed to Public!")
            
    page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\tiktok_final_status.png")
    browser.close()
    print("[+] Done checking TikTok Studio.")
