import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import List, Optional
import imageio_ffmpeg

logger = logging.getLogger("VideoAssemblyService")

class VideoAssemblyService:
    """Production-grade video concatenation and assembly service with orphan process cleanup and error recovery."""

    def __init__(self, output_dir: Optional[str] = None):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.output_dir = Path(output_dir) if output_dir else base_dir / "data" / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    def merge_story_parts(self, story_id: str, part_filepaths: List[str]) -> str:
        """Assembles list of video clips into a single high-quality short."""
        if not part_filepaths:
            raise ValueError(f"No video files provided to merge for story {story_id}")

        for p in part_filepaths:
            if not os.path.exists(p) or os.path.getsize(p) == 0:
                raise FileNotFoundError(f"Missing or empty part file: {p}")

        out_filepath = str(self.output_dir / f"{story_id}_final.mp4")
        concat_txt = str(self.output_dir / f"{story_id}_concat.txt")

        logger.info(f"[ASSEMBLER] Merging {len(part_filepaths)} clips for {story_id} -> {out_filepath}")

        # Create concat demuxer file
        with open(concat_txt, "w", encoding="utf-8") as f:
            for fp in part_filepaths:
                clean_path = fp.replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        # Step 1: Attempt fast stream-copy concat (no re-encoding, zero CPU/RAM bottleneck)
        cmd_copy = [
            self.ffmpeg_exe, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_txt,
            "-c", "copy",
            out_filepath
        ]

        try:
            res = subprocess.run(cmd_copy, capture_output=True, text=True, timeout=120)
            if res.returncode == 0 and os.path.exists(out_filepath) and os.path.getsize(out_filepath) > 50000:
                logger.info(f"[ASSEMBLER] Stream-copy assembly succeeded: {out_filepath}")
                self._cleanup_temp_file(concat_txt)
                return out_filepath
        except Exception as e:
            logger.warning(f"[ASSEMBLER] Stream copy attempt notice ({e}), falling back to standard re-encode...")

        # Step 2: Fallback re-encode if timestamps/codecs differ slightly
        cmd_reencode = [
            self.ffmpeg_exe, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_txt,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-crf", "20",
            "-c:a", "aac",
            "-b:a", "192k",
            out_filepath
        ]

        res = subprocess.run(cmd_reencode, capture_output=True, text=True, timeout=180)
        self._cleanup_temp_file(concat_txt)

        if res.returncode != 0 or not os.path.exists(out_filepath) or os.path.getsize(out_filepath) == 0:
            raise RuntimeError(f"FFMPEG assembly failed for {story_id}: {res.stderr[:300]}")

        logger.info(f"[ASSEMBLER] Assembly completed successfully: {out_filepath}")
        return out_filepath

    @staticmethod
    def _cleanup_temp_file(filepath: str):
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass
