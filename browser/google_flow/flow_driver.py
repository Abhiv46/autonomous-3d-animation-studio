import time
import os
import re
from typing import Dict, Any, Optional
from playwright.sync_api import Page


class GenerationOutcomeUncertain(RuntimeError):
    """A prompt was submitted, but the generated result could not be saved locally."""


class GoogleFlowProjectLockedDriver:
    """Enforces strict project locking: NEVER automatically creates a new project. Opens existing configured project or halts with structured error."""
    
    def __init__(self, raw_clips_dir: str):
        self.raw_clips_dir = raw_clips_dir
        os.makedirs(raw_clips_dir, exist_ok=True)

    def open_configured_project(
        self,
        page: Page,
        slot_index: int,
        project_id: Optional[str],
        project_name: Optional[str],
        expected_email: str,
    ) -> bool:
        """Verifies the isolated profile account, then opens the configured project."""
        base_account_url = "https://flow.google.com/"
        editor_selector = "[contenteditable='true']:visible, div.ProseMirror:visible, textarea:visible"

        page.goto(base_account_url, wait_until="domcontentloaded", timeout=40000)
        page.wait_for_timeout(1500)
        signed_in_account = page.get_by_role(
            "button",
            name=re.compile(re.escape(expected_email), re.IGNORECASE),
        )
        if signed_in_account.count() == 0:
            raise PermissionError(
                f"Flow automation profile for account slot {slot_index} is not signed in as "
                f"{expected_email}. Sign into that account in its dedicated profile."
            )

        # Flow's /u/ index is unrelated to our configured account slot.
        if project_id:
            target_url = f"https://flow.google.com/project/{project_id}"
            try:
                page.goto(target_url, wait_until="domcontentloaded", timeout=40000)
                page.wait_for_timeout(4000)
                self._clear_overlays(page)
                if project_id in page.url and page.locator(editor_selector).count() > 0:
                    return True
            except Exception:
                pass

        # Fall back to the signed-in account's home and locate only the configured project.
        page.goto(base_account_url, wait_until="domcontentloaded", timeout=40000)
        page.wait_for_timeout(4000)
        self._clear_overlays(page)

        if project_id:
            project_link = page.locator(f"a[href*='/project/{project_id}']").first
            if project_link.count() > 0 and project_link.is_visible():
                try:
                    project_link.click(force=True, timeout=5000)
                    page.wait_for_timeout(4000)
                    if project_id in page.url and page.locator(editor_selector).count() > 0:
                        return True
                except Exception:
                    pass

        if project_name:
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
                        if (
                            (not project_id or project_id in page.url)
                            and page.locator(editor_selector).count() > 0
                        ):
                            return True
                    except Exception:
                        continue

        raise FileNotFoundError(
            f"Configured project (ID: {project_id}, Name: '{project_name}') was not available "
            f"in the signed-in Flow profile for account slot {slot_index}. "
            "Strict project lock policy prevented creating a new project."
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
        """Dispatches once, waits for a newly-created render, and downloads its 720p video."""
        page.keyboard.press("Escape")
        page.wait_for_timeout(400)

        editor = page.locator("flow-rich-text-editor div.ProseMirror, div.ProseMirror, [contenteditable='true']")
        if editor.count() == 0:
            raise RuntimeError("Prompt editor textarea not found on Google Flow canvas.")

        cards = page.locator("[aria-label*='Open video in editor' i], video")
        existing_card_count = cards.count()
        tiles = page.locator("flow-grid-tile-container")
        existing_tile_count = tiles.count()

        editor.first.click()
        page.wait_for_timeout(300)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        page.keyboard.type(prompt_text, delay=5)
        page.wait_for_timeout(800)

        send_btn = page.locator("button:has-text('arrow_forward'), button[aria-label*='Start generation' i]")
        if send_btn.count() > 0 and send_btn.first.is_visible():
            send_btn.first.click(force=True)
        else:
            page.keyboard.press("Enter")

        try:
            for _ in range(12):
                time.sleep(1)
                if self.handle_normal_operational_questions(page):
                    break

            start_time = time.time()
            target_tile = None
            while (time.time() - start_time) < timeout_seconds:
                time.sleep(5)
                failed_msg = page.get_by_text("Failed", exact=True)
                if failed_msg.count() > 0 and failed_msg.first.is_visible():
                    raise RuntimeError("Google Flow reported a failed render.")

                cards = page.locator("[aria-label*='Open video in editor' i], video")
                if cards.count() > existing_card_count:
                    target_tile = page.locator("flow-grid-tile-container").last
                    break

                current_tiles = page.locator("flow-grid-tile-container")
                if current_tiles.count() > existing_tile_count:
                    target_tile = current_tiles.last
                    break

            if target_tile is None:
                raise TimeoutError(
                    f"No new render appeared within {timeout_seconds} seconds after submission."
                )

            target_tile.click(force=True)
            page.wait_for_timeout(2500)

            dl_btn = page.locator(
                "button[aria-label*='Download media' i], button[aria-label*='Download' i]"
            ).first
            if dl_btn.count() == 0 or not dl_btn.is_visible():
                raise RuntimeError("Download control for the new render was not found.")
            dl_btn.click(force=True)
            page.wait_for_timeout(1000)

            target_720 = page.get_by_text("720p", exact=True).first
            if target_720.count() == 0:
                target_720 = page.get_by_role("menuitem", name="720p")
            if target_720.count() == 0:
                raise RuntimeError("720p download option was not found.")

            out_path = os.path.join(self.raw_clips_dir, out_filename)
            with page.expect_download(timeout=45000) as dl_info:
                target_720.click(force=True)
            download = dl_info.value
            download.save_as(out_path)
            if not os.path.isfile(out_path) or os.path.getsize(out_path) == 0:
                raise RuntimeError("Flow download completed without a usable local video file.")

            back_btn = page.locator(
                "button[aria-label='Back'], [aria-label='Navigate back'], "
                "button:has-text('arrow_back'), button:has-text('Done')"
            ).first
            if back_btn.count() > 0 and back_btn.is_visible():
                back_btn.click(force=True)
            else:
                page.keyboard.press("Escape")
            page.wait_for_timeout(1000)
            return out_path
        except Exception as exc:
            raise GenerationOutcomeUncertain(
                "The prompt was submitted, but the render/download result is uncertain. "
                "Review the existing Flow project before retrying."
            ) from exc
