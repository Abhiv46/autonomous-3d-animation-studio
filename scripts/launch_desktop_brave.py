import subprocess
import time
import win32process

subprocess.run(["taskkill", "/F", "/IM", "brave.exe"], capture_output=True)
time.sleep(1)

si = win32process.STARTUPINFO()
si.lpDesktop = r"WinSta0\Default"

exe = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
args = (
    f'"{exe}" '
    r'--remote-debugging-port=9222 '
    r'--user-data-dir="C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data" '
    r'"https://flow.google.com/u/0/project/1876f0f7-bc42-4764-86c9-35d76cb3a615"'
)

hProcess, hThread, dwProcessId, dwThreadId = win32process.CreateProcess(
    None, args, None, None, False, 0, None, None, si
)
print("Spawned Brave with remote debugging on WinSta0\\Default! PID:", dwProcessId)
