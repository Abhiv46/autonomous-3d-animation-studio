from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

# Let's inspect the original 'The Naughty Duo' project on Slot 0 and Slot 2
def inspect_original():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        # Slot 0 original project
        url0 = "https://flow.google.com/u/0/project/1876f0f7-bc42-4764-86c9-35d76cb3a615"
        page.goto(url0, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\original_tnd_slot0.png")
        print(f"Slot 0 Original Project: {url0} inspected")

        # Slot 2 original project
        url2 = "https://flow.google.com/u/2/project/0fa549b9-b73f-4dac-8061-365fd0498eb2"
        page.goto(url2, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        page.screenshot(path=r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\original_tnd_slot2.png")
        print(f"Slot 2 Original Project: {url2} inspected")

        browser.close()

if __name__ == "__main__":
    inspect_original()
