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
    
    # Let's inspect the DOM elements with class containing 'item' or 'card' or 'asset'
    elements = page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('*'));
        return els.filter(el => {
            const rect = el.getBoundingClientRect();
            return rect.width > 100 && rect.height > 100 && rect.left > 150 && rect.right < 1400 && rect.top > 80;
        }).map(el => ({
            tag: el.tagName,
            cls: el.className,
            text: el.innerText ? el.innerText.substring(0, 50) : '',
            rect: {left: el.getBoundingClientRect().left, top: el.getBoundingClientRect().top, w: el.getBoundingClientRect().width, h: el.getBoundingClientRect().height}
        })).slice(0, 20);
    }""")
    print(f"Canvas element candidates: {len(elements)}")
    for e in elements[:10]:
        print(e)
        
    # Also find video src or any media URLs
    media_urls = page.evaluate("""() => {
        const imgs = Array.from(document.querySelectorAll('img')).map(i => i.src);
        const vids = Array.from(document.querySelectorAll('video')).map(v => v.src);
        return {imgs: imgs.slice(0, 10), vids: vids};
    }""")
    print("Media URLs:", media_urls)

    ctx.close()
