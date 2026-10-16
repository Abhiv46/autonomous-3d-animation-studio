import sys
import os
import subprocess
import time
import win32process
from playwright.sync_api import sync_playwright

print("[1] Restarting Brave with remote-debugging-port=9222...")
subprocess.run(["taskkill", "/F", "/IM", "brave.exe"], capture_output=True)
time.sleep(2)

si = win32process.STARTUPINFO()
si.lpDesktop = r"WinSta0\Default"

exe = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
args = (
    f'"{exe}" '
    r'--remote-debugging-port=9222 '
    r'--user-data-dir="C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data" '
    r'--restore-last-session'
)

win32process.CreateProcess(None, args, None, None, False, 0, None, None, si)
print("Spawned Brave with CDP port 9222. Waiting 5s...")
time.sleep(5)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    print(f"CDP connected successfully! Active tabs: {len(context.pages)}")
    for page in context.pages:
        print("Tab:", page.title(), "->", page.url)
