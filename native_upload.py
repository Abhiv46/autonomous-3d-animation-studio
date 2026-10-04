import time
import threading
import win32gui
import win32con
from pathlib import Path
from playwright.sync_api import sync_playwright

VIDEO_FILE = str(Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\TheNaughtyDuo_GoodHabits_Master.mp4").resolve())

def handle_open_dialog():
    print("[Thread] Waiting for Open dialog...")
    for _ in range(30):
        # Find window with title 'Open'
        hwnd = win32gui.FindWindow("#32770", "Open")
        if hwnd:
            print(f"[Thread] Found Open dialog! HWND: {hwnd}")
            time.sleep(0.5)
            # Find the Edit control inside the dialog
            # In modern Windows file dialogs, it is inside ComboBoxEx32 -> ComboBox -> Edit
            edit_hwnd = None
            def enum_children(child_hwnd, _):
                nonlocal edit_hwnd
                cls = win32gui.GetClassName(child_hwnd)
                if cls == "Edit":
                    edit_hwnd = child_hwnd
            win32gui.EnumChildWindows(hwnd, enum_children, None)
            
            if edit_hwnd:
                print(f"[Thread] Found Edit HWND: {edit_hwnd}")
                # Set text
                win32gui.SendMessage(edit_hwnd, win32con.WM_SETTEXT, None, VIDEO_FILE)
                time.sleep(0.5)
                # Press Enter or click Open button
                win32gui.PostMessage(edit_hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                win32gui.PostMessage(edit_hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
                print("[Thread] Sent file path and pressed Enter!")
                return True
        time.sleep(0.5)
    print("[Thread] Timeout waiting for Open dialog.")
    return False

# Start handler thread
t = threading.Thread(target=handle_open_dialog)
t.start()

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    
    print("[Main] Clicking Select files button...")
    page.locator("#select-files-button").first.click()
    
    t.join(timeout=20)
    print("[Main] Dialog handled! Waiting 10s for upload to initialize...")
    time.sleep(10)
    
    page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\after_native_upload.png")
    print("[Main] Screenshot saved!")
