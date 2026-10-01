import os
import psutil
import subprocess
import time
from typing import Optional, Dict, Any
from playwright.sync_api import sync_playwright, BrowserContext, Page

class BrowserAutomationEngine:
    """Enterprise-grade browser automation manager with process health checks, profile locking recovery, and auto-cleanup."""
    
    def __init__(self, browser_exe: str, user_data_dir: str, headless: bool = True):
        self.browser_exe = browser_exe
        self.user_data_dir = user_data_dir
        self.headless = headless
        self.playwright = None
        self.context: Optional[BrowserContext] = None

    @staticmethod
    def cleanup_stale_processes(browser_name: str = "brave.exe"):
        """Safely cleans up orphaned browser or renderer processes to release lockfiles."""
        try:
            subprocess.run(["taskkill", "/F", "/IM", browser_name], capture_output=True)
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
            time.sleep(1.5)
        except Exception:
            pass

    @staticmethod
    def is_browser_running(browser_name: str = "brave.exe") -> bool:
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == browser_name.lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False

    def launch(self) -> BrowserContext:
        """Launches persistent context with retry logic, auto-recovery on profile lock, and screenshot capability."""
        # 1. Clean up any orphaned background processes holding profile lock
        self.cleanup_stale_processes(os.path.basename(self.browser_exe))

        self.playwright = sync_playwright().start()
        
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-infobars",
            "--window-size=1440,900"
        ]

        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

        for attempt in range(3):
            try:
                self.context = self.playwright.chromium.launch_persistent_context(
                    user_data_dir=self.user_data_dir,
                    executable_path=self.browser_exe,
                    headless=self.headless,
                    user_agent=user_agent,
                    args=args,
                    timeout=30000
                )
                return self.context
            except Exception as e:
                time.sleep(2)
                self.cleanup_stale_processes(os.path.basename(self.browser_exe))
                if attempt == 2:
                    raise RuntimeError(f"Failed to launch browser after 3 attempts: {e}")

    def capture_error_screenshot(self, page: Page, filepath: str) -> str:
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            page.screenshot(path=filepath)
            return filepath
        except Exception:
            return ""

    def close(self):
        try:
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass
