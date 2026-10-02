from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(user_data_dir=BRAVE_DATA, executable_path=BRAVE_EXE, headless=True)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.set_viewport_size({"width": 1600, "height": 1000})
    page.goto("https://flow.google.com/u/0/project/1876f0f7-bc42-4764-86c9-35d76cb3a615", wait_until="domcontentloaded")
    page.wait_for_timeout(3500)

    # Click Add ingredients to the prompt box
    add_btn = page.locator("button[aria-label='Add ingredients to the prompt box']")
    print("Clicking Add ingredients to prompt box...")
    add_btn.click()
    page.wait_for_timeout(2000)
    page.screenshot(path="data/test_add_ingredients_popup.png")

    # Click kaavya
    kaavya_opt = page.locator("text='kaavya'").first
    if kaavya_opt.count() > 0:
        print("Found kaavya option, clicking...")
        kaavya_opt.click()
        page.wait_for_timeout(1500)
        page.screenshot(path="data/test_kaavya_selected.png")
        # Click Add to prompt
        add_to_prompt = page.locator("button:has-text('Add to prompt')").first
        if add_to_prompt.count() > 0:
            print("Clicking Add to prompt...")
            add_to_prompt.click()
            page.wait_for_timeout(1500)
            page.screenshot(path="data/test_kaavya_added.png")

    ctx.close()
