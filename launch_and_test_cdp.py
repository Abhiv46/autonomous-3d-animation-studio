import subprocess
import time
import win32process
from playwright.sync_api import sync_playwright

print("[1] Restarting Brave with remote debugging port 9222...")
subprocess.run(["taskkill", "/F", "/IM", "brave.exe"], capture_output=True)
time.sleep(1.5)

si = win32process.STARTUPINFO()
si.lpDesktop = r"WinSta0\Default"

exe = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
args = (
    f'"{exe}" '
    r'--remote-debugging-port=9222 '
    r'--user-data-dir="C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data" '
    r'--restore-last-session '
    r'"https://studio.youtube.com"'
)

hProcess, hThread, dwProcessId, dwThreadId = win32process.CreateProcess(
    None, args, None, None, False, 0, None, None, si
)
print("Spawned Brave! PID:", dwProcessId)
time.sleep(3)

# Test CDP connection
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    print(f"CDP connected! Active pages: {len(context.pages)}")
    for page in context.pages:
        print("Page URL:", page.url)
