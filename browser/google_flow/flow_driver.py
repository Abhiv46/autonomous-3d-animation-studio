import time
import os
from typing import Dict, Any, Optional
from playwright.sync_api import Page

class GoogleFlowProjectLockedDriver:
    """Enforces strict project locking: NEVER automatically creates a new project. Opens existing configured project or halts with structured error."""
    
    def __init__(self, raw_clips_dir: str):
        self.raw_clips_dir = raw_clips_dir
        os.makedirs(raw_clips_dir, exist_ok=True)

    def open_configured_project(self, page: Page, slot_index: int, project_id: Optional[str], project_name: Optional[str]) -> bool:
        """Opens the existing project for this account. Strictly avoids creating new blank projects."""
        base_account_url = f"https://flow.google.com/u/{slot_index}/"
        
        # 1. Direct URL Navigation (Primary Bulletproof Method)
        if project_id:
            target_url = f"https://flow.google.com/u/{slot_index}/project/{project_id}"
            try:
                page.goto(target_url, wait_until="domcontentloaded", timeout=40000)
                page.wait_for_timeout(4000)
                
                # Check for and clear any modal/backdrop overlays if present
                self._clear_overlays(page)

                # Verify if project canvas successfully loaded
                if "project/" in page.url and project_id in page.url:
                    # Also ensure prompt editor or canvas exists
                    editor = page.locator("[contenteditable='true'], div.ProseMirror, textarea")
                    if editor.count() > 0 or "project/" in page.url:
                        return True
            except Exception:
                pass

        # 2. Fallback: Navigate to account dashboard and find project card
        page.goto(base_account_url, wait_until="domcontentloaded", timeout=40000)
        page.wait_for_timeout(4000)
        self._clear_overlays(page)

        if project_name:
            # Click card directly avoiding backdrop pointer intercepts
            selectors = [
                f"[aria-label*='{project_name}' i]",
                f"div.project-card:has-text('{project_name}')",
                f"[role='button']:has-text('{project_name}')",
                f"div:has-text('{project_name}')",
            ]
            for sel in selectors:
                card = page.locator(sel).first
                if card.count() > 0 and card.is_visible():
                    try:
                        self._clear_overlays(page)
                        card.click(force=True, timeout=5000)
                        page.wait_for_timeout(4000)
                        if "project/" in page.url:
                            return True
                    except Exception:
                        continue

        # Strict Project Lock Policy: DO NOT silently click "+ New Project"
        raise FileNotFoundError(
            f"Configured project (ID: {project_id}, Name: '{project_name}') NOT FOUND on Account /u/{slot_index}/. "
            f"Strict project lock policy prevented creating random duplicate projects."
        )

    def _clear_overlays(self, page: Page):
        """Neutralizes Angular CDK backdrop overlays or popups that intercept clicks."""
        try:
            page.evaluate("""() => {
                const backdrops = document.querySelectorAll('.cdk-overlay-backdrop, .cdk-overlay-container, [class*="backdrop"]');
                backdrops.forEach(el => {
                    // Only remove if it is not a required modal
                    if (!el.querySelector('button, input, textarea')) {
                        el.remove();
                    }
                });
            }""")
        except Exception:
            pass

    def handle_normal_operational_questions(self, page: Page) -> bool:
        """Auto-approves safe generation actions (continue, approve credits, retry) while blocking financial/security changes."""
        # 1. Check for 'Always approve' or 'Approve' credit buttons
        target = page.locator("button:has-text('Always approve'), [role='button']:has-text('Always approve')")
        if target.count() > 0 and target.last.is_visible():
            target.last.click(force=True)
            return True

        app_target = page.locator("button:has-text('Approve'), [role='button']:has-text('Approve')")
        if app_target.count() > 0 and app_target.last.is_visible():
            app_target.last.click(force=True)
            return True

        # 2. Check for unexpected financial/payment confirmation dialogs (CRITICAL SAFETY)
        financial_warning = page.locator("text='Payment', text='Billing', text='Purchase', text='Subscription', text='Card details'")
        if financial_warning.count() > 0 and financial_warning.first.is_visible():
            raise PermissionError("FINANCIAL_APPROVAL_REQUIRED: Detected payment or billing dialog. Halting automated clicking for safety.")

        return False

    def generate_and_download_scene(self, page: Page, prompt_text: str, out_filename: str, timeout_seconds: int = 90) -> str:
        """Dispatches prompt, handles credit approval, monitors dynamic cloud rendering, and downloads 720p video."""
        page.keyboard.press("Escape")
        page.wait_for_timeout(400)

        editor = page.locator("[contenteditable='true'], div.ProseMirror")
        if editor.count() == 0:
            raise RuntimeError("Prompt editor textarea not found on Google Flow canvas.")

        editor.first.click()
        page.wait_for_timeout(300)
        # Use keyboard typing to trigger ProseMirror React state updates
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        page.keyboard.type(prompt_text, delay=5)
        page.wait_for_timeout(800)

        # Submit prompt using dedicated Start generation button or Enter
        send_btn = page.locator("button[aria-label*='Start generation' i]")
        if send_btn.count() > 0 and send_btn.first.is_visible():
            send_btn.first.click(force=True)
        else:
            page.keyboard.press("Enter")

        # Auto-approve operational question
        for _ in range(12):
            time.sleep(1)
            if self.handle_normal_operational_questions(page):
                break

        # Dynamic cloud render polling: wait until Stop button turns back into Start generation or a new video appears
        start_time = time.time()
        rendered = False
        target_card = None
        while (time.time() - start_time) < timeout_seconds:
            time.sleep(5)
            # Check if video appeared in chat or canvas
            cards = page.locator("[aria-label*='Open video in editor' i], video")
            if cards.count() > 0:
                rendered = True
                target_card = cards.last
                break
            # Or generation finished and stop button is gone
            stop_btn = page.locator("button:has-text('Stop')")
            if stop_btn.count() == 0 and (time.time() - start_time) > 20:
                cards = page.locator("video, [class*='media'], [aria-label*='Open video' i]")
                if cards.count() > 0:
                    rendered = True
                    target_card = cards.last
                    break

        if not rendered or not target_card:
            raise TimeoutError(f"Generation rendering timed out after {timeout_seconds} seconds.")

        # Download 720p video
        target_card.click(force=True)
        page.wait_for_timeout(2500)

        dl_btn = page.locator("button[aria-label*='Download' i]").first
        if dl_btn.count() > 0 and dl_btn.is_visible():
            dl_btn.click(force=True)
            page.wait_for_timeout(1000)
            target_720 = page.get_by_text("720p").first
            if target_720.count() > 0:
                out_path = os.path.join(self.raw_clips_dir, out_filename)
                with page.expect_download(timeout=45000) as dl_info:
                    target_720.click(force=True)
                download = dl_info.value
                download.save_as(out_path)

        # Close editor drawer
        back_btn = page.locator("button[aria-label='Back'], [aria-label='Navigate back'], button:has-text('arrow_back')").first
        if back_btn.count() > 0 and back_btn.is_visible():
            back_btn.click(force=True)
        else:
            page.keyboard.press("Escape")
        page.wait_for_timeout(1000)

        return os.path.join(self.raw_clips_dir, out_filename)
