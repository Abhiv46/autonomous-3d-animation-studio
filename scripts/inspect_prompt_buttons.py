from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(user_data_dir=BRAVE_DATA, executable_path=BRAVE_EXE, headless=True)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.set_viewport_size({"width": 1600, "height": 1000})
    page.goto("https://flow.google.com/u/0/project/1876f0f7-bc42-4764-86c9-35d76cb3a615", wait_until="domcontentloaded")
    page.wait_for_timeout(3500)

    # Check if inside editor, click Done if so
    done_btn = page.locator("button:has-text('Done')").first
    if done_btn.count() > 0 and done_btn.is_visible():
        print("Clicking Done to exit video editor...")
        done_btn.click()
        page.wait_for_timeout(2000)

    # Inspect all buttons around the prompt box
    prompt_container = page.locator(".chat-input, .prompt-input, [class*='prompt-box'], [class*='chat-container'], [class*='bottom']").all()
    print("Prompt containers found:", len(prompt_container))

    all_buttons = page.locator("button").all()
    print(f"Total buttons on page: {len(all_buttons)}")
    for idx, b in enumerate(all_buttons):
        aria = b.get_attribute("aria-label") or ""
        txt = b.inner_text().strip().replace("\n", " ")
        if any(k in (aria + txt).lower() for k in ["add", "ingredient", "media", "character", "create", "send", "submit", "arrow"]):
            print(f"Button {idx}: aria='{aria}' text='{txt}'")

    ctx.close()
