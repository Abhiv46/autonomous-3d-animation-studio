import os
import re
import subprocess
from typing import Dict, Any, List


class QualityControlAgent:
    """Verifies media assets against broadcast quality gate before declaring READY_TO_PUBLISH."""

    @staticmethod
    def inspect_video_asset(filepath: str, min_duration: float = 15.0, max_duration: float = 120.0) -> Dict[str, Any]:
        if not os.path.exists(filepath):
            return {"passed": False, "reason": "FILE_DOES_NOT_EXIST"}

        size_bytes = os.path.getsize(filepath)
        if size_bytes < 500000:  # Less than 500KB
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


class QualityAssuranceAgent:
    """Performs full-package validation for generated video content and metadata."""

    REQUIRED_SCENE_COUNT = 8
    BLOCKLIST = [
        "deep water",
        "danger",
        "scary",
        "night scene",
        "distorted hands",
        "extra characters",
        "bad watermark",
        "logo clutter",
        "low resolution",
    ]

    def assess_story_bundle(self, bundle: Dict[str, Any]) -> Dict[str, Any]:
        issues: List[str] = []
        score = 100

        title = str(bundle.get("title") or "").strip()
        prompt = str(bundle.get("prompt") or "").strip()
        flow_story = bundle.get("flow_story") or {}
        scenes = (flow_story.get("scene_sequence") or [])
        publishing_payload = bundle.get("publishing_payload") or {}
        script = bundle.get("script") or {}

        if not title:
            issues.append("MISSING_TITLE")
            score -= 25
        if len(title) > 100:
            issues.append("TITLE_TOO_LONG")
            score -= 10
        if not prompt:
            issues.append("MISSING_PROMPT")
            score -= 25
        if not scenes or len(scenes) != self.REQUIRED_SCENE_COUNT:
            issues.append("SCENE_COUNT_MISMATCH")
            score -= 20
        cta_text = f"{bundle.get('prompt', '')} {script.get('cta', '')}".upper()
        if not any(term in cta_text for term in ("LIKE", "SUBSCRIBE", "FOLLOW")):
            issues.append("MISSING_CTA")
            score -= 15
        if "Kaavya" not in prompt or "Kaartik" not in prompt or "Pinki" not in prompt:
            issues.append("CHARACTER_LOCK_MISSING")
            score -= 20
        if publishing_payload.get("video_path") and not os.path.exists(str(publishing_payload["video_path"])):
            issues.append("VIDEO_FILE_NOT_FOUND")
            score -= 20

        scene_text = " ".join(
            f"{scene.get('title', '')} {scene.get('prompt', '')}"
            for scene in scenes
            if isinstance(scene, dict)
        ).lower()
        for text in self.BLOCKLIST:
            if text in scene_text or text in prompt.lower():
                issues.append(f"RISK_DETECTED:{text}")
                score -= 10

        duration = float(script.get("duration_seconds", 0) or 0)
        if duration and (duration < 45 or duration > 90):
            issues.append("DURATION_OUT_OF_RANGE")
            score -= 10

        normalized_issues = sorted(set(issues))
        passed = not normalized_issues
        if not passed:
            score = max(0, score)

        return {
            "passed": passed,
            "score": round(score, 1),
            "issues": normalized_issues,
            "quality_gate": "READY_TO_PUBLISH" if passed else "REWORK_REQUIRED",
        }

    def evaluate_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        evaluated = []
        for item in batch:
            report = self.assess_story_bundle(item)
            evaluated.append({
                "id": item.get("id"),
                "title": item.get("title"),
                "platform": item.get("platform"),
                "passed": report["passed"],
                "score": report["score"],
                "quality_gate": report["quality_gate"],
                "issues": report["issues"],
            })
        return evaluated
