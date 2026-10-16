from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from browser.engine.browser_manager import BrowserAutomationEngine
from browser.engine.pinned_brave import DEFAULT_CDP_ENDPOINT, select_google_account


@dataclass(frozen=True)
class FlowCreditSnapshot:
    email: str
    credits: int
    refresh_label: str
    checked_at: str
    next_refresh_at: Optional[str]


def parse_credit_snapshot(
    page_text: str,
    expected_email: str,
    now: Optional[datetime] = None,
) -> FlowCreditSnapshot:
    if expected_email.casefold() not in page_text.casefold():
        raise PermissionError(
            f"Google Flow page is not authenticated as the configured account {expected_email}."
        )

    credit_match = re.search(r"\b(\d+)\s+Google Flow credits?\b", page_text, re.IGNORECASE)
    if not credit_match:
        raise ValueError("Could not verify a Google Flow credit balance from the account panel.")

    refresh_match = re.search(
        r"\bCredits refresh daily at\s+([^\r\n]+)",
        page_text,
        re.IGNORECASE,
    )
    refresh_label = refresh_match.group(1).strip() if refresh_match else "Not shown by Flow"
    observed_at = now or datetime.now().astimezone()
    next_refresh = _next_local_refresh(refresh_label, observed_at)

    return FlowCreditSnapshot(
        email=expected_email,
        credits=int(credit_match.group(1)),
        refresh_label=refresh_label,
        checked_at=observed_at.isoformat(timespec="seconds"),
        next_refresh_at=next_refresh.isoformat(timespec="seconds") if next_refresh else None,
    )


def _next_local_refresh(label: str, now: datetime) -> Optional[datetime]:
    parsed = None
    for time_format in ("%I:%M %p", "%I %p"):
        try:
            parsed = datetime.strptime(label, time_format).time()
            break
        except ValueError:
            continue
    if parsed is None:
        return None

    local_now = now.astimezone()
    next_refresh = local_now.replace(
        hour=parsed.hour,
        minute=parsed.minute,
        second=0,
        microsecond=0,
    )
    if next_refresh <= local_now:
        next_refresh += timedelta(days=1)
    return next_refresh


class GoogleFlowCreditMonitor:
    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)

    def inspect(self, account: dict, headless: bool = True) -> FlowCreditSnapshot:
        slot = int(account["slot_index"])
        engine = BrowserAutomationEngine(headless=False)
        page = None
        try:
            context = engine.connect_over_cdp(os.getenv("FLOW_CDP_ENDPOINT", DEFAULT_CDP_ENDPOINT))
            page = context.new_page()
            expected_email = str(account["email"])
            select_google_account(page, expected_email)
            page.wait_for_timeout(1500)

            project_id = account.get("project_id")
            if project_id and page.locator(f"a[href*='/project/{project_id}']").count() == 0:
                raise FileNotFoundError(
                    f"Configured Flow project {project_id} is not visible for slot {slot}; "
                    "the monitor will not switch projects."
                )

            body_text = page.locator("body").inner_text()
            if not re.search(r"\b\d+\s+Google Flow credits?\b", body_text, re.IGNORECASE):
                page.get_by_role("button", name=re.compile("Account details", re.IGNORECASE)).click()
                page.wait_for_timeout(500)
                body_text = page.locator("body").inner_text()
            return parse_credit_snapshot(body_text, expected_email)
        except PlaywrightTimeoutError as exc:
            raise TimeoutError(f"Timed out while reading the live Flow account panel: {exc}") from exc
        except PlaywrightError as exc:
            raise RuntimeError(f"Could not read the live Flow account panel: {exc}") from exc
        finally:
            if page is not None and not page.is_closed():
                page.close()
            engine.close()
