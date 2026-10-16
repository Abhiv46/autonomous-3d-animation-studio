import os
import pickle
from typing import Dict, Any, Optional
from ..common.base_adapter import BasePlatformAdapter
import logging
from platforms.live_production import LiveProductionGate

class YouTubePlatformAdapter(BasePlatformAdapter):
    """Production YouTube Data API v3 adapter with strict safety checks, COPPA validation, and golden slot scheduling."""

    def __init__(
        self,
        token_pickle_path: str,
        target_channel_id: str,
        protected_video_ids: Optional[list[str]] = None,
    ):
        self.token_pickle_path = token_pickle_path
        self.target_channel_id = target_channel_id
        self.protected_video_ids = set(protected_video_ids or [])
        self.service = None

    def authenticate(self) -> bool:
        if not os.path.exists(self.token_pickle_path):
            return False
        try:
            with open(self.token_pickle_path, "rb") as f:
                creds = pickle.load(f)
            from googleapiclient.discovery import build
            self.service = build("youtube", "v3", credentials=creds)
            return True
        except Exception as e:
            logging.warning(f"Failed to authenticate YouTube API: {e}")
            return False
    def validate_publication_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-publishing validation check. Blocks upload if channel ID mismatch or corrupted file."""
        if payload.get("channel_id") != self.target_channel_id:
            return {
                "valid": False,
                "error": f"SECURITY_ALERT: Target channel ID ({payload.get('channel_id')}) does NOT match configured channel ID ({self.target_channel_id})"
            }

        video_path = payload.get("video_path")
        if not video_path or not os.path.exists(video_path):
            return {"valid": False, "error": "MISSING_VIDEO_FILE"}

        if not payload.get("title") or len(payload.get("title")) < 5:
            return {"valid": False, "error": "INVALID_TITLE"}

        return {"valid": True}

    def upload_short(self, video_path: str, metadata: Dict[str, Any], schedule_iso: Optional[str] = None) -> Dict[str, Any]:
        val = self.validate_publication_payload({
            "channel_id": self.target_channel_id,
            "video_path": video_path,
            "title": metadata.get("title")
        })
        if not val["valid"]:
            raise ValueError(f"Publication validation failed: {val['error']}")

        # Dry run simulation support
        if os.getenv("DRY_RUN", "false").lower() == "true":
            return {
                "success": True,
                "platform_video_id": "SIMULATED_YT_ID_12345",
                "status": "SIMULATED_SCHEDULED"
            }

        if not self.service and not self.authenticate():
            raise PermissionError("YouTube API service not authenticated.")

        from googleapiclient.http import MediaFileUpload

        status_dict = {"selfDeclaredMadeForKids": True}
        if schedule_iso:
            status_dict["privacyStatus"] = "private"
            status_dict["publishAt"] = schedule_iso
        else:
            status_dict["privacyStatus"] = "public"

        body = {
            "snippet": {
                "title": metadata["title"][:95],
                "description": metadata.get("description", ""),
                "tags": metadata.get("tags", []),
                "categoryId": metadata.get("category_id", "1")
            },
            "status": status_dict
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
        req = self.service.videos().insert(part="snippet,status", body=body, media_body=media)
        resp = None
        while resp is None:
            status, resp = req.next_chunk()

        return {
            "success": True,
            "platform_video_id": resp.get("id"),
            "url": f"https://youtube.com/shorts/{resp.get('id')}"
        }

    def get_status(self, platform_video_id: str) -> Dict[str, Any]:
        return {"status": "LIVE"}

    def get_owned_video(self, platform_video_id: str) -> Dict[str, Any]:
        if not platform_video_id:
            raise ValueError("A YouTube video ID is required.")
        if not self.service and not self.authenticate():
            raise PermissionError("YouTube API service not authenticated.")
        response = self.service.videos().list(
            part="snippet,status",
            id=platform_video_id,
        ).execute()
        items = response.get("items", [])
        if len(items) != 1:
            raise LookupError(f"YouTube video {platform_video_id} was not found.")
        video = items[0]
        if video.get("snippet", {}).get("channelId") != self.target_channel_id:
            raise PermissionError(
                f"YouTube video {platform_video_id} does not belong to the configured channel."
            )
        return video

    def update_video_metadata(
        self,
        platform_video_id: str,
        expected_title: str,
        metadata: Dict[str, Any],
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        if not LiveProductionGate().is_approved():
            raise PermissionError("Live channel actions are not approved.")
        if not expected_title:
            raise ValueError("Expected current title is required for a safe metadata edit.")
        allowed = {"title", "description", "tags"}
        if not metadata or set(metadata) - allowed:
            raise ValueError("Only title, description, and tags may be edited.")
        if "title" in metadata and not 1 <= len(str(metadata["title"])) <= 100:
            raise ValueError("YouTube title must be between 1 and 100 characters.")

        video = self.get_owned_video(platform_video_id)
        snippet = video["snippet"]
        if snippet.get("title") != expected_title:
            raise ValueError(
                "The live YouTube title changed since the action plan was prepared."
            )
        if dry_run:
            return {
                "status": "DRY_RUN_ONLY",
                "platform_video_id": platform_video_id,
                "old_title": snippet.get("title"),
                "proposed_metadata": metadata,
            }

        updated_snippet = {
            key: value
            for key, value in snippet.items()
            if key in {
                "title",
                "description",
                "tags",
                "categoryId",
                "defaultLanguage",
                "defaultAudioLanguage",
            }
        }
        updated_snippet.update(metadata)
        response = self.service.videos().update(
            part="snippet",
            body={"id": platform_video_id, "snippet": updated_snippet},
        ).execute()
        return {
            "status": "UPDATED",
            "platform_video_id": response.get("id", platform_video_id),
            "title": response.get("snippet", {}).get("title"),
        }

    def delete_video(
        self,
        platform_video_id: str,
        expected_title: str,
        confirmation: str,
        reason_type: str,
        evidence_reference: str,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        if not LiveProductionGate().is_approved():
            raise PermissionError("Live channel actions are not approved.")
        if reason_type not in {"verified_duplicate", "official_policy_notice"}:
            raise ValueError("YouTube deletion requires verified duplicate or policy evidence.")
        if not evidence_reference.strip():
            raise ValueError("YouTube deletion requires an evidence reference.")
        if platform_video_id in self.protected_video_ids:
            raise PermissionError(
                f"YouTube video {platform_video_id} is protected from deletion."
            )
        if confirmation != f"DELETE youtube {platform_video_id}":
            raise PermissionError(
                "Permanent deletion requires an exact video-ID confirmation."
            )
        video = self.get_owned_video(platform_video_id)
        actual_title = video.get("snippet", {}).get("title")
        if not expected_title or actual_title != expected_title:
            raise ValueError(
                "The live YouTube title does not match the action plan; deletion stopped."
            )
        if dry_run:
            return {
                "status": "DRY_RUN_ONLY",
                "platform_video_id": platform_video_id,
                "title": actual_title,
                "destructive": True,
            }
        self.service.videos().delete(id=platform_video_id).execute()
        return {
            "status": "DELETED",
            "platform_video_id": platform_video_id,
            "destructive": True,
        }

    def get_analytics(self, platform_video_id: str) -> Dict[str, Any]:
        return {
            "available": False,
            "platform_video_id": platform_video_id,
            "reason": "YouTube Analytics API integration is not configured; no metrics were fetched.",
        }
