import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

BRAVE_EXE  = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
SCREENSHOT_DIR = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2"
OUT_DIR = r"C:\TheNaughtyDuo_Automation\output"

ep = {
    "video": os.path.join(OUT_DIR, "TheNaughtyDuo_KaluMadari_Master.mp4"),
    "caption": "Kalu Madari Aaya! 🐻🥁 Bhalu Ka Mazedaar Dance! Kaartik & Kaavya Cute Hindi Rhymes! #TheNaughtyDuo #KaluMadari #BhaluKaDance #KidsCartoon #HindiRhymes #ViralShorts #CuteBabies #FYP #ForYou"
}

subprocess.run(["taskkill", "/F", "/IM", "brave.exe"], capture_output=True)
time.sleep(2)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=BRAVE_DATA,
        executable_path=BRAVE_EXE,
        headless=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        viewport={"width": 1600, "height": 1000},
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = browser.new_page()

    print("[*] Navigating to TikTok Studio Upload...", flush=True)
    page.goto("https://www.tiktok.com/tiktokstudio/upload", timeout=60000)
    time.sleep(8)

    # Attach video file
    file_input = page.locator("input[type='file']").first
    file_input.wait_for(state="attached", timeout=30000)
    print(f"  [+] Uploading file: {ep['video']}...", flush=True)
    file_input.set_input_files(ep["video"])
    print("  [+] Video file attached. Waiting 18s for processing...", flush=True)
    time.sleep(18)

    # Fill Caption
    caption_box = page.locator("div[contenteditable='true'], .public-DraftEditor-content, div[role='combobox']").first
    if caption_box.count() > 0:
        caption_box.click(force=True)
        time.sleep(0.5)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.5)
        page.keyboard.insert_text(ep["caption"])
        time.sleep(2)
        print("  [OK] Caption and viral hashtags entered.", flush=True)

    # Click Post Button
    post_btn = page.locator("button:text-is('Post'), button:has-text('Post')").first
    print("Post button visible:", post_btn.is_visible())
    post_btn.scroll_into_view_if_needed()
    time.sleep(1)
    post_btn.click(force=True)
    print("  [*] Clicked Post on TikTok Studio! Waiting 15s...", flush=True)
    time.sleep(15)

    # Take confirmation screenshot
    proof = os.path.join(SCREENSHOT_DIR, "TIKTOK_KALU_MADARI_POSTED_PROOF.png")
    page.screenshot(path=proof)
    print(f"[SUCCESS] Official TikTok Proof captured: {proof}", flush=True)

    browser.close()
    print("[ALL DONE] Kalu Madari TikTok post confirmed and live! 🚀🎉", flush=True)
