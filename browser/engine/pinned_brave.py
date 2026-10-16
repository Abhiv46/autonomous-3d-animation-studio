from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse
from pathlib import Path
from typing import Optional

import psutil
from playwright.sync_api import Page


DEFAULT_CDP_ENDPOINT = "http://127.0.0.1:9222"
DEFAULT_CDP_PORT = 9222
ACCOUNT_CHOOSER_URL = (
    "https://accounts.google.com/AccountChooser"
    "?continue=https%3A%2F%2Fflow.google.com%2F"
)


def _browser_info(endpoint: str) -> Optional[dict]:
    try:
        with urllib.request.urlopen(f"{endpoint}/json/version", timeout=2) as response:
            return json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return None


def _is_brave_listener(endpoint: str) -> bool:
    port = urlparse(endpoint).port
    if port is None:
        return False
    try:
        connections = psutil.net_connections(kind="tcp")
    except psutil.Error as exc:
        raise RuntimeError(f"Could not verify the owner of local browser port {port}: {exc}") from exc
    for connection in connections:
        if (
            connection.status == psutil.CONN_LISTEN
            and connection.laddr
            and connection.laddr.port == port
            and connection.pid
        ):
            try:
                executable = psutil.Process(connection.pid).exe()
            except psutil.Error as exc:
                raise RuntimeError(
                    f"Could not verify the process listening on local browser port {port}: {exc}"
                ) from exc
            return Path(executable).name.casefold() == "brave.exe"
    return False


def ensure_pinned_brave(
    browser_exe: Optional[str] = None,
    endpoint: str = DEFAULT_CDP_ENDPOINT,
    startup_timeout: int = 30,
) -> None:
    """Use the default pinned Brave profile; never close or replace a running browser."""
    existing = _browser_info(endpoint)
    if existing:
        if not _is_brave_listener(endpoint):
            raise RuntimeError(
                f"Port {endpoint} belongs to a different browser; refusing to attach."
            )
        return

    brave_processes = [
        proc for proc in psutil.process_iter(["name", "cmdline"])
        if (proc.info.get("name") or "").casefold() == "brave.exe"
    ]
    if brave_processes:
        raise RuntimeError(
            "Brave is already open but its pinned profile was not started with remote debugging. "
            "Close Brave normally, then rerun this command; it will reopen the same default "
            "Brave profile with local automation enabled."
        )

    executable = browser_exe or os.getenv(
        "BRAVE_EXECUTABLE",
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    )
    if not Path(executable).is_file():
        raise FileNotFoundError(
            f"Pinned Brave executable not found at {executable}; set BRAVE_EXECUTABLE."
        )

    local_app_data = os.getenv("LOCALAPPDATA")
    if not local_app_data:
        raise EnvironmentError("LOCALAPPDATA is unavailable; cannot locate the pinned Brave profile.")
    user_data_dir = Path(local_app_data) / "BraveSoftware" / "Brave-Browser" / "User Data"
    user_data_dir.mkdir(parents=True, exist_ok=True)

    subprocess.Popen(
        [
            executable,
            f"--user-data-dir={user_data_dir}",
            "--profile-directory=Default",
            f"--remote-debugging-port={DEFAULT_CDP_PORT}",
            "--no-first-run",
            "https://flow.google.com/",
        ],
        cwd=str(Path(executable).parent),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    deadline = time.monotonic() + startup_timeout
    while time.monotonic() < deadline:
        info = _browser_info(endpoint)
        if info:
            if not _is_brave_listener(endpoint):
                raise RuntimeError(f"Port {endpoint} became available for a non-Brave browser.")
            return
        time.sleep(1)
    raise TimeoutError(
        "Pinned Brave started, but its remote-debugging endpoint did not become available. "
        "No profile data was copied or reset."
    )


def select_google_account(page: Page, email: str) -> None:
    """Selects an already signed-in Google identity in the pinned browser."""
    import re

    page.goto(ACCOUNT_CHOOSER_URL, wait_until="domcontentloaded", timeout=40000)
    identity = page.get_by_text(re.compile(rf"^{re.escape(email)}$", re.IGNORECASE)).first
    try:
        identity.wait_for(state="visible", timeout=15000)
    except Exception as exc:
        raise PermissionError(
            f"{email} is not available in the pinned Brave Google account chooser."
        ) from exc

    identity.click(timeout=10000)
    try:
        page.wait_for_url(
            lambda url: url.startswith("https://flow.google.com/"),
            timeout=30000,
        )
        page.locator("body").wait_for(timeout=20000)
    except Exception as exc:
        raise RuntimeError(
            f"Google did not return to Flow after selecting {email}; "
            "a sign-in or account verification step may need human attention."
        ) from exc

    account_button = page.get_by_role(
        "button",
        name=re.compile(re.escape(email), re.IGNORECASE),
    )
    try:
        account_button.wait_for(state="visible", timeout=20000)
    except Exception as exc:
        raise PermissionError(
            f"Flow did not confirm the selected Google identity {email}."
        ) from exc
