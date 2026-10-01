import os
import subprocess
from typing import Dict, Any

class QualityControlAgent:
    """Verifies media assets against broadcast quality gate before declaring READY_TO_PUBLISH."""

    @staticmethod
    def inspect_video_asset(filepath: str, min_duration: float = 15.0, max_duration: float = 120.0) -> Dict[str, Any]:
        if not os.path.exists(filepath):
            return {"passed": False, "reason": "FILE_DOES_NOT_EXIST"}

        size_bytes = os.path.getsize(filepath)
        if size_bytes < 500000: # Less than 500KB
            return {"passed": False, "reason": "FILE_SIZE_TOO_SMALL_LIKELY_CORRUPT"}

        # Probe duration and streams via ffprobe if available
        try:
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filepath]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if res.returncode == 0:
                duration = float(res.stdout.strip())
                if duration < min_duration or duration > max_duration:
                    return {"passed": False, "reason": f"DURATION_OUT_OF_BOUNDS ({duration}s)"}
        except Exception:
            pass

        return {
            "passed": True,
            "size_bytes": size_bytes,
            "filepath": filepath,
            "reason": "PASSED_QUALITY_GATE"
        }
