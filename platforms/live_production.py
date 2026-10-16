from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List


class LiveProductionGate:
    """Blocks live publishing unless credentials, files, and explicit approval are present."""

    def __init__(self, config: Dict[str, Any] | None = None, repo_root: str | None = None):
        self.config = config or {}
        self.repo_root = Path(repo_root or Path(__file__).resolve().parents[1])

    def _default_paths(self) -> Dict[str, str]:
        configured_client_secret = self.repo_root / "config" / "client_secret.json"
        discovered_client_secret = self.repo_root.parent / "client_secrets.json"
        client_secret = (
            configured_client_secret
            if configured_client_secret.is_file()
            else discovered_client_secret
        )
        return {
            "youtube_token": str(self.repo_root / "config" / "token.pickle"),
            "youtube_client_secret": str(client_secret),
            "live_approval_file": str(self.repo_root / "config" / "live_publish_approved.txt"),
        }

    def inspect(self) -> Dict[str, Any]:
        paths = self._default_paths()
        env_overrides = {
            "youtube_token": os.getenv("YOUTUBE_TOKEN_PICKLE_PATH", paths["youtube_token"]),
            "youtube_client_secret": os.getenv("YOUTUBE_CLIENT_SECRET_PATH", paths["youtube_client_secret"]),
            "live_approval_file": os.getenv("LIVE_APPROVAL_FILE", paths["live_approval_file"]),
        }

        reasons: List[str] = []
        ready = True

        if not self.is_approved(env_overrides["live_approval_file"]):
            reasons.append("LIVE_PUBLISH_APPROVED is not enabled")
            ready = False

        for name, path in env_overrides.items():
            exists = os.path.exists(path)
            if name.endswith("approval_file"):
                if not exists:
                    reasons.append(f"Missing live approval file: {path}")
                    ready = False
                continue
            if not exists:
                reasons.append(f"Missing required credential file: {path}")
                ready = False

        if not self.config.get("platforms", {}).get("youtube", {}).get("enabled", True):
            reasons.append("YouTube platform is disabled in config")
            ready = False
        tiktok_config = self.config.get("platforms", {}).get("tiktok", {})
        if tiktok_config.get("enabled", False) and not tiktok_config.get("channel_handle"):
            reasons.append("TikTok channel_handle is not configured")
            ready = False

        return {
            "ready": ready,
            "status": "READY" if ready else "BLOCKED",
            "reasons": reasons,
            "paths": env_overrides,
            "approval_required": True,
        }

    def is_approved(self, approval_path: str | None = None) -> bool:
        env_approved = os.getenv("LIVE_PUBLISH_APPROVED", "false").strip().lower() in {
            "1",
            "true",
            "yes",
            "y",
        }
        path = Path(
            approval_path
            or os.getenv("LIVE_APPROVAL_FILE", self._default_paths()["live_approval_file"])
        )
        file_approved = (
            path.is_file()
            and path.read_text(encoding="utf-8").strip().casefold() == "approved"
        )
        return env_approved or file_approved

    def write_approval_file(self, approval_path: str | None = None) -> Dict[str, Any]:
        path = Path(approval_path or self._default_paths()["live_approval_file"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("approved\n", encoding="utf-8")
        os.environ["LIVE_PUBLISH_APPROVED"] = "true"
        return {"approved": True, "path": str(path)}


__all__ = ["LiveProductionGate"]
