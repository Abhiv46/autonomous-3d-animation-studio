from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from platforms.live_production import LiveProductionGate
from platforms.tiktok.tiktok_adapter import TikTokPlatformAdapter
from platforms.youtube.youtube_adapter import YouTubePlatformAdapter


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class ChannelDoctorActionExecutor:
    """Executes explicitly planned channel actions with target and approval checks."""

    def __init__(self, config: dict[str, Any], repo_root: str | Path):
        self.config = config
        self.repo_root = Path(repo_root)
        youtube = config.get("platforms", {}).get("youtube", {})
        self.youtube = YouTubePlatformAdapter(
            token_pickle_path=str(self.repo_root / "config" / "token.pickle"),
            target_channel_id=youtube.get("channel_id", ""),
            protected_video_ids=youtube.get("protected_videos", []),
        )
        tiktok = config.get("platforms", {}).get("tiktok", {})
        self.tiktok = TikTokPlatformAdapter(tiktok.get("channel_handle"))
        self.gate = LiveProductionGate(config=config, repo_root=str(self.repo_root))

    def execute(self, plan: dict[str, Any], dry_run: bool = True) -> dict[str, Any]:
        actions = plan.get("actions")
        if not isinstance(actions, list):
            raise ValueError("Action plan must include an actions list.")
        results = []
        for index, action in enumerate(actions):
            try:
                self._validate_action(action, dry_run)
                results.append(
                    self._run_action(action, dry_run)
                )
            except (KeyError, PermissionError, ValueError, LookupError) as exc:
                results.append(
                    {
                        "index": index,
                        "platform": action.get("platform") if isinstance(action, dict) else None,
                        "operation": action.get("operation") if isinstance(action, dict) else None,
                        "status": "BLOCKED",
                        "reason": str(exc),
                    }
                )
        return {
            "mode": "dry_run" if dry_run else "live",
            "results": results,
            "live_actions_performed": any(
                item.get("status") in {"UPDATED", "DELETED", "LIVE_POSTED"}
                for item in results
            ),
        }

    def _validate_action(self, action: Any, dry_run: bool) -> None:
        if not isinstance(action, dict):
            raise ValueError("Each action must be an object.")
        platform = action.get("platform")
        operation = action.get("operation")
        video_id = str(action.get("video_id") or "")
        expected_title = action.get("expected_title")
        if platform not in {"youtube", "tiktok"}:
            raise ValueError("Unsupported platform.")
        if not video_id or not expected_title:
            raise ValueError("An exact video_id and expected_title are required.")
        if platform == "youtube" and not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            raise ValueError("Invalid YouTube video ID.")
        if platform == "tiktok" and not re.fullmatch(r"\d{15,25}", video_id):
            raise ValueError("Invalid TikTok video ID.")
        if operation == "update_metadata":
            if platform != "youtube":
                raise ValueError(
                    "TikTok post-publication caption edits are not supported by Studio."
                )
            metadata = action.get("metadata")
            if not isinstance(metadata, dict):
                raise ValueError("Metadata update requires a metadata object.")
            if set(metadata) - {"title", "description", "tags"} or not metadata:
                raise ValueError("Only title, description, and tags may be updated.")
        elif operation == "update_caption":
            if platform != "tiktok":
                raise ValueError("update_caption is only valid for TikTok.")
            raise ValueError(
                "TikTok Studio does not expose post-publication caption editing."
            )
        elif operation == "delete":
            if action.get("reason_type") not in {
                "verified_duplicate",
                "official_policy_notice",
            }:
                raise ValueError(
                    "Delete is limited to a verified duplicate or official platform policy notice."
                )
            if not str(action.get("evidence_reference") or "").strip():
                raise ValueError("Deletion requires an evidence reference.")
            if action["reason_type"] == "verified_duplicate":
                duplicate_id = str(action.get("duplicate_video_id") or "")
                duplicate_title = str(action.get("duplicate_expected_title") or "")
                source_path = Path(str(action.get("source_path") or ""))
                duplicate_source_path = Path(
                    str(action.get("duplicate_source_path") or "")
                )
                if platform == "youtube" and not re.fullmatch(
                    r"[A-Za-z0-9_-]{11}", duplicate_id
                ):
                    raise ValueError("Verified duplicate deletion needs its peer video ID.")
                if platform == "tiktok" and not re.fullmatch(
                    r"\d{15,25}", duplicate_id
                ):
                    raise ValueError("Verified duplicate deletion needs its peer video ID.")
                if duplicate_id == video_id or not duplicate_title:
                    raise ValueError("Duplicate peer must be a different, titled video.")
                if not source_path.is_file() or not duplicate_source_path.is_file():
                    raise ValueError(
                        "Verified duplicate deletion needs both original source files."
                    )
                if _file_sha256(source_path) != _file_sha256(duplicate_source_path):
                    raise ValueError(
                        "The two original source files do not have identical SHA-256 fingerprints."
                    )
            if action.get("confirmation") != f"DELETE {platform} {video_id}":
                raise PermissionError(
                    "Permanent deletion requires exact platform and video-ID confirmation."
                )
            if platform == "youtube" and video_id in self.youtube.protected_video_ids:
                raise PermissionError("This YouTube video is protected from deletion.")
        else:
            raise ValueError("Unsupported action operation.")

        if not dry_run and not self.gate.is_approved():
            raise PermissionError("Live channel actions are not approved.")

    def _run_action(self, action: dict[str, Any], dry_run: bool) -> dict[str, Any]:
        platform = action["platform"]
        operation = action["operation"]
        video_id = action["video_id"]
        if platform == "youtube":
            if operation == "update_metadata":
                result = self.youtube.update_video_metadata(
                    video_id,
                    action["expected_title"],
                    action["metadata"],
                    dry_run=dry_run,
                )
            else:
                if action.get("reason_type") == "verified_duplicate":
                    duplicate = self.youtube.get_owned_video(action["duplicate_video_id"])
                    if duplicate.get("snippet", {}).get("title") != action[
                        "duplicate_expected_title"
                    ]:
                        raise ValueError(
                            "The live duplicate peer title changed since the plan was prepared."
                        )
                result = self.youtube.delete_video(
                    video_id,
                    action["expected_title"],
                    action["confirmation"],
                    action["reason_type"],
                    action["evidence_reference"],
                    dry_run=dry_run,
                )
        elif operation == "delete":
            from scripts.tiktok_studio_uploader import manage_tiktok_video

            duplicate_video_id = None
            duplicate_caption = None
            if action.get("reason_type") == "verified_duplicate":
                duplicate_video_id = action["duplicate_video_id"]
                duplicate_caption = action["duplicate_expected_title"]
            result = manage_tiktok_video(
                operation="delete",
                video_id=video_id,
                expected_handle=self.tiktok.target_account_handle or "",
                expected_caption=action["expected_title"],
                confirmation=action["confirmation"],
                reason_type=action["reason_type"],
                evidence_reference=action["evidence_reference"],
                duplicate_video_id=duplicate_video_id,
                duplicate_expected_caption=duplicate_caption,
                dry_run=dry_run,
            )
        else:
            result = {
                "success": False,
                "status": "UNSUPPORTED_PLATFORM_ACTION",
                "reason": "TikTok post-publication caption editing is unavailable.",
            }
        return {
            "platform": platform,
            "operation": operation,
            "video_id": video_id,
            **result,
        }


def load_action_plan(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Action plan must be a JSON object.")
    return value
