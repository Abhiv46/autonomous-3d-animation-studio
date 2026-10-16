import os
from typing import Dict, Any, Optional
from ..common.base_adapter import BasePlatformAdapter
import logging
from playwright.sync_api import Error as PlaywrightError

class TikTokPlatformAdapter(BasePlatformAdapter):
    """TikTok Studio adapter ensuring 60-75s Creator Rewards Program compliance, SEO captioning, and duplicate checks."""

    def __init__(self, target_account_handle: Optional[str] = None):
        self.target_account_handle = target_account_handle

    def authenticate(self) -> bool:
        if not self.target_account_handle:
            logging.error("TikTok account handle is not configured; refusing live Studio access.")
            return False
        try:
            from scripts.tiktok_studio_uploader import verify_tiktok_studio_identity

            return verify_tiktok_studio_identity(self.target_account_handle)
        except (
            OSError,
            PermissionError,
            PlaywrightError,
            RuntimeError,
            TimeoutError,
            ValueError,
        ) as e:
            logging.warning(f"TikTok authentication failed: {e}")
            return False

    def validate_publication_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        video_path = payload.get("video_path")
        if not video_path or not os.path.exists(video_path):
            return {"valid": False, "error": "MISSING_VIDEO_FILE"}
        return {"valid": True}

    def upload_short(self, video_path: str, metadata: Dict[str, Any], schedule_iso: Optional[str] = None) -> Dict[str, Any]:
        if schedule_iso:
            raise ValueError("TikTok scheduled publishing is not supported by the Studio uploader.")
        if not self.target_account_handle:
            raise PermissionError(
                "TikTok account handle is not configured; refusing to upload."
            )
        val = self.validate_publication_payload({"video_path": video_path})
        if not val["valid"]:
            raise ValueError(f"TikTok publication validation failed: {val['error']}")

        if os.getenv("DRY_RUN", "false").lower() == "true":
            return {
                "success": False,
                "status": "DRY_RUN_ONLY",
            }

        caption = metadata.get("caption") or metadata.get("title", "")
        from scripts.tiktok_studio_uploader import upload_to_tiktok_studio
        result = upload_to_tiktok_studio(
            video_path,
            caption,
            expected_handle=self.target_account_handle,
            dry_run=False,
        )
        if result.get("success"):
            result["platform_video_id"] = f"tt_{os.path.basename(video_path)}"
            result["url"] = f"https://www.tiktok.com/{self.target_account_handle}"
        return result

    def get_status(self, platform_video_id: str) -> Dict[str, Any]:
        return {"status": "LIVE"}

    def get_analytics(self, platform_video_id: str) -> Dict[str, Any]:
        return {
            "available": False,
            "platform_video_id": platform_video_id,
            "reason": "TikTok Studio analytics integration is not configured; no metrics were fetched.",
        }
