from __future__ import annotations

import logging
import os
import re
import unicodedata
from typing import Any
from urllib.parse import urlparse

from playwright.sync_api import Error as PlaywrightError, sync_playwright

from browser.engine.pinned_brave import DEFAULT_CDP_ENDPOINT, ensure_pinned_brave
from platforms.live_production import LiveProductionGate

logger = logging.getLogger(__name__)


def _normalize_visible_text(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value)
    return " ".join(
        "".join(char for char in normalized if unicodedata.category(char) != "Cf").split()
    )


def tiktok_identity_matches(
    expected_handle: str,
    profile_hrefs: list[str],
    visible_text: str,
) -> bool:
    if not re.fullmatch(r"@[A-Za-z0-9._]+", expected_handle or ""):
        return False

    expected = expected_handle.casefold()
    for href in profile_hrefs:
        path = urlparse(href).path if "://" in href else href
        profile_handle = re.match(r"^/(@[^/?]+)", path)
        if profile_handle and profile_handle.group(1).casefold() == expected:
            return True

    handle_pattern = re.compile(
        rf"(?<![A-Za-z0-9._]){re.escape(expected_handle)}(?![A-Za-z0-9._])",
        re.IGNORECASE,
    )
    return bool(handle_pattern.search(visible_text or ""))


def _visible_tiktok_identity(page, expected_handle: str) -> bool:
    profile_hrefs = page.locator("a[href*='/@']").evaluate_all(
        "(links) => links.map((link) => link.href)"
    )
    return tiktok_identity_matches(
        expected_handle,
        profile_hrefs,
        page.locator("body").inner_text(),
    )


def verify_tiktok_studio_identity(
    expected_handle: str,
    endpoint: str = DEFAULT_CDP_ENDPOINT,
) -> bool:
    if not re.fullmatch(r"@[A-Za-z0-9._]+", expected_handle or ""):
        raise ValueError("A verified TikTok handle is required before Studio access.")

    ensure_pinned_brave(endpoint=endpoint)
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(endpoint, timeout=10000)
        if not browser.contexts:
            raise RuntimeError("Pinned Brave has no available browser context.")
        page = browser.contexts[0].new_page()
        try:
            page.goto(
                "https://www.tiktok.com/tiktokstudio/content",
                wait_until="domcontentloaded",
                timeout=45000,
            )
            page.locator("body").wait_for(timeout=20000)
            if "login" in page.url.casefold():
                raise PermissionError("TikTok Studio requires sign-in in pinned Brave.")
            if not _visible_tiktok_identity(page, expected_handle):
                raise PermissionError(
                    f"TikTok Studio did not verify the configured account {expected_handle}."
                )
            return True
        finally:
            page.close()


def upload_to_tiktok_studio(
    video_path: str,
    caption_text: str,
    expected_handle: str | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    if not os.path.exists(video_path):
        return {"success": False, "status": "MISSING_VIDEO_FILE"}
    if not re.fullmatch(r"@[A-Za-z0-9._]+", expected_handle or ""):
        return {"success": False, "status": "TIKTOK_HANDLE_NOT_CONFIGURED"}
    if not dry_run and not LiveProductionGate().is_approved():
        return {"success": False, "status": "LIVE_PUBLISH_NOT_APPROVED"}

    try:
        ensure_pinned_brave()
        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(
                DEFAULT_CDP_ENDPOINT,
                timeout=10000,
            )
            if not browser.contexts:
                raise RuntimeError("Pinned Brave has no available browser context.")
            page = browser.contexts[0].new_page()
            try:
                page.goto(
                    "https://www.tiktok.com/tiktokstudio/content",
                    wait_until="domcontentloaded",
                    timeout=45000,
                )
                page.locator("body").wait_for(timeout=20000)

                if "login" in page.url.casefold():
                    return {"success": False, "status": "TIKTOK_SESSION_EXPIRED"}
                if not _visible_tiktok_identity(page, expected_handle):
                    return {
                        "success": False,
                        "status": "TIKTOK_ACCOUNT_IDENTITY_MISMATCH",
                        "expected_handle": expected_handle,
                    }
                if dry_run:
                    return {
                        "success": False,
                        "status": "DRY_RUN_ONLY",
                        "identity_verified": True,
                        "expected_handle": expected_handle,
                    }

                page.goto(
                    "https://www.tiktok.com/tiktokstudio/upload?from=upload",
                    wait_until="domcontentloaded",
                    timeout=45000,
                )
                page.locator("body").wait_for(timeout=20000)
                if "login" in page.url.casefold():
                    return {"success": False, "status": "TIKTOK_SESSION_EXPIRED"}

                file_input = page.locator("input[type='file']").first
                if file_input.count() == 0:
                    for frame in page.frames:
                        candidate = frame.locator("input[type='file']")
                        if candidate.count() > 0:
                            file_input = candidate.first
                            break
                if file_input.count() == 0:
                    return {"success": False, "status": "TIKTOK_UPLOAD_INPUT_NOT_FOUND"}

                file_input.set_input_files(video_path)
                page.wait_for_timeout(10000)
                caption_box = page.locator(
                    "[contenteditable='true'], .public-DraftEditor-content, textarea"
                ).first
                if caption_box.count() == 0:
                    return {"success": False, "status": "TIKTOK_CAPTION_INPUT_NOT_FOUND"}
                caption_box.click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                page.keyboard.type(caption_text, delay=8)

                post_button = page.get_by_role("button", name="Post", exact=True)
                if post_button.count() == 0:
                    return {"success": False, "status": "TIKTOK_POST_BUTTON_UNAVAILABLE"}
                post_button.last.wait_for(state="visible", timeout=15000)
                if post_button.last.is_disabled():
                    return {"success": False, "status": "TIKTOK_POST_BUTTON_DISABLED"}

                post_button.last.click()
                try:
                    page.get_by_text(
                        re.compile(
                            r"(posted successfully|video has been posted|post submitted)",
                            re.IGNORECASE,
                        )
                    ).wait_for(state="visible", timeout=20000)
                except PlaywrightError:
                    return {
                        "success": False,
                        "status": "SUBMISSION_UNCONFIRMED",
                        "message": (
                            "TikTok submission may have completed; verify Studio before retrying."
                        ),
                    }
                return {
                    "success": True,
                    "status": "LIVE_POSTED",
                    "account_handle": expected_handle,
                }
            finally:
                page.close()
    except (
        PlaywrightError,
        OSError,
        PermissionError,
        RuntimeError,
        TimeoutError,
        ValueError,
    ) as exc:
        logger.error("TikTok Studio operation failed: %s", exc)
        return {"success": False, "status": "FAILED", "error": str(exc)}


def manage_tiktok_video(
    operation: str,
    video_id: str,
    expected_handle: str,
    expected_caption: str,
    confirmation: str,
    reason_type: str | None = None,
    evidence_reference: str | None = None,
    duplicate_video_id: str | None = None,
    duplicate_expected_caption: str | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    if operation == "update_caption":
        return {
            "success": False,
            "status": "UNSUPPORTED_PLATFORM_ACTION",
            "reason": "TikTok Studio does not expose post-publication caption editing.",
        }
    if operation != "delete":
        return {"success": False, "status": "UNSUPPORTED_OPERATION"}
    if not re.fullmatch(r"\d{15,25}", video_id or ""):
        return {"success": False, "status": "INVALID_TIKTOK_VIDEO_ID"}
    if not re.fullmatch(r"@[A-Za-z0-9._]+", expected_handle or ""):
        return {"success": False, "status": "TIKTOK_HANDLE_NOT_CONFIGURED"}
    if not expected_caption:
        return {"success": False, "status": "EXPECTED_CAPTION_REQUIRED"}
    if duplicate_video_id is not None and (
        not re.fullmatch(r"\d{15,25}", duplicate_video_id)
        or duplicate_video_id == video_id
        or not duplicate_expected_caption
    ):
        return {"success": False, "status": "DUPLICATE_PEER_INVALID"}
    if confirmation != f"DELETE tiktok {video_id}":
        return {"success": False, "status": "DELETE_CONFIRMATION_REQUIRED"}
    if reason_type not in {"verified_duplicate", "official_policy_notice"}:
        return {"success": False, "status": "DELETE_EVIDENCE_REQUIRED"}
    if not str(evidence_reference or "").strip():
        return {"success": False, "status": "DELETE_EVIDENCE_REQUIRED"}
    if not dry_run and not LiveProductionGate().is_approved():
        return {"success": False, "status": "LIVE_PUBLISH_NOT_APPROVED"}

    try:
        ensure_pinned_brave()
        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(
                DEFAULT_CDP_ENDPOINT,
                timeout=10000,
            )
            if not browser.contexts:
                raise RuntimeError("Pinned Brave has no available browser context.")
            page = browser.contexts[0].new_page()
            try:
                page.goto(
                    "https://www.tiktok.com/tiktokstudio/content",
                    wait_until="domcontentloaded",
                    timeout=45000,
                )
                page.get_by_text(re.compile(r"\bPosts\s+\d+"), exact=False).wait_for(
                    state="visible",
                    timeout=25000,
                )
                if "login" in page.url.casefold():
                    return {"success": False, "status": "TIKTOK_SESSION_EXPIRED"}
                post_links = page.locator(f"a[href*='/video/{video_id}']")
                post_links.first.wait_for(state="visible", timeout=25000)
                if not _visible_tiktok_identity(page, expected_handle):
                    return {
                        "success": False,
                        "status": "TIKTOK_ACCOUNT_IDENTITY_MISMATCH",
                        "expected_handle": expected_handle,
                    }
                target_url = f"https://www.tiktok.com/{expected_handle}/video/{video_id}"
                target_url = f"https://www.tiktok.com/{expected_handle}/video/{video_id}"
                matching_links = post_links.evaluate_all(
                    "(links, expected) => links.filter((link) => link.href === expected).length",
                    target_url,
                )
                if matching_links != 1:
                    return {
                        "success": False,
                        "status": "TIKTOK_TARGET_NOT_UNIQUE",
                        "video_id": video_id,
                    }
                post_link = post_links.first
                row = post_link.locator(
                    "xpath=ancestor::div[.//button[@data-tt='components_ActionCell_Clickable']][1]"
                )
                if row.count() != 1:
                    return {"success": False, "status": "TIKTOK_TARGET_ROW_NOT_FOUND"}
                actual_caption = post_link.inner_text().strip()
                if _normalize_visible_text(actual_caption) != _normalize_visible_text(
                    expected_caption
                ):
                    return {
                        "success": False,
                        "status": "TIKTOK_TARGET_CHANGED",
                        "actual_caption": actual_caption,
                    }
                if duplicate_video_id is not None:
                    duplicate_url = (
                        f"https://www.tiktok.com/{expected_handle}/video/{duplicate_video_id}"
                    )
                    duplicate_links = page.locator(
                        f"a[href*='/video/{duplicate_video_id}']"
                    )
                    duplicate_matches = duplicate_links.evaluate_all(
                        "(links, expected) => links.filter((link) => link.href === expected).length",
                        duplicate_url,
                    )
                    if (
                        duplicate_matches != 1
                        or _normalize_visible_text(duplicate_links.first.inner_text())
                        != _normalize_visible_text(duplicate_expected_caption)
                    ):
                        return {
                            "success": False,
                            "status": "TIKTOK_DUPLICATE_PEER_CHANGED_OR_MISSING",
                        }
                if dry_run:
                    return {
                        "success": False,
                        "status": "DRY_RUN_ONLY",
                        "identity_verified": True,
                        "video_id": video_id,
                        "caption": actual_caption,
                        "destructive": True,
                    }

                row.get_by_role("button").last.click()
                page.get_by_text("Delete", exact=True).last.click()
                dialog = page.get_by_role("dialog")
                if dialog.count() != 1:
                    return {
                        "success": False,
                        "status": "DELETE_CONFIRMATION_UNVERIFIED",
                    }
                dialog_text = dialog.inner_text()
                if expected_caption not in dialog_text:
                    return {
                        "success": False,
                        "status": "DELETE_TARGET_CONFIRMATION_MISMATCH",
                    }
                confirm_button = dialog.get_by_role(
                    "button",
                    name="Delete",
                    exact=True,
                )
                if confirm_button.count() != 1:
                    return {
                        "success": False,
                        "status": "DELETE_CONFIRMATION_BUTTON_UNVERIFIED",
                    }
                confirm_button.click()
                try:
                    dialog.wait_for(state="hidden", timeout=15000)
                except PlaywrightError:
                    return {
                        "success": False,
                        "status": "DELETE_RESULT_UNCONFIRMED",
                        "message": "Verify the TikTok post in Studio before retrying.",
                    }
                return {
                    "success": True,
                    "status": "DELETED",
                    "account_handle": expected_handle,
                    "video_id": video_id,
                }
            finally:
                page.close()
    except (
        PlaywrightError,
        OSError,
        PermissionError,
        RuntimeError,
        TimeoutError,
        ValueError,
    ) as exc:
        logger.error("TikTok Studio video action failed: %s", exc)
        return {"success": False, "status": "FAILED", "error": str(exc)}
