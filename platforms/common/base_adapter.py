from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BasePlatformAdapter(ABC):
    """Abstract interface for all content publication platforms (YouTube, TikTok, Instagram, etc.)."""

    @abstractmethod
    def authenticate(self) -> bool:
        pass

    @abstractmethod
    def validate_publication_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Strict machine-readable validation before attempting any upload."""
        pass

    @abstractmethod
    def upload_short(self, video_path: str, metadata: Dict[str, Any], schedule_iso: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_status(self, platform_video_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_analytics(self, platform_video_id: str) -> Dict[str, Any]:
        pass
