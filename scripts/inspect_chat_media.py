import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
brave_exe = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
brave_data = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=brave_data,
        executable_path=brave_exe,
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    url = "https://flow.google.com/u/3/project/a1c6f19b-b046-41f3-9b33-fbc756646163"
    page = ctx.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(6000)
    
    # 1. Open session 2 "Playful Pixar Style Story"
    menu_icon = page.locator("button:has-text('menu'), [aria-label*='Sessions']").first
    menu_icon.click(force=True)
    page.wait_for_timeout(1000)
    s2 = page.locator("text='Playful Pixar Style Story'").first
    s2.click(force=True)
    page.wait_for_timeout(3000)
    
    # In Session 2, look at the media item inside chat
    # In session2_check_latest.png there is a media thumbnail with play icon inside chat!
    # Let's inspect all buttons or images inside the chat panel
    panel = page.locator("mat-sidenav, flow-chat-panel, div[class*='drawer-content']").last
    media_in_chat = panel.locator("div:has(> img), div:has(> video), [role='button']").all()
    print("Media elements in S2 drawer:", len(media_in_chat))
    
    # Let's see what happens if we click on that image in chat
    img_in_chat = panel.locator("img").first
    if img_in_chat.count() > 0:
        print("Clicking img in chat...")
        img_in_chat.click(force=True)
        page.wait_for_timeout(3000)
        page.screenshot(path=str(BASE_DIR / "data" / "chat_img_clicked.png"))
        
        # Check download buttons now
        for b in page.locator("button").all():
            if b.is_visible():
                txt = b.inner_text().strip()
                aria = b.get_attribute("aria-label") or ""
                if any(w in (txt + aria).lower() for w in ["download", "export", "720", "1080", "mp4"]):
                    print(f"DL Option: txt='{txt}', aria='{aria}'")

    ctx.close()
