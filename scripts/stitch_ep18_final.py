import os
import sys
import subprocess
from pathlib import Path
import imageio_ffmpeg

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
OUTPUT_DIR = BASE_DIR / "data" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

c1 = RAW_CLIPS / "ep_18_scene_01.mp4"
c2 = RAW_CLIPS / "ep_18_scene_02.mp4"
c3 = RAW_CLIPS / "ep_18_scene_03.mp4"

out_final = OUTPUT_DIR / "ep_18_magic_freeze_remote_final.mp4"
concat_list = RAW_CLIPS / "ep18_concat.txt"

with open(concat_list, "w", encoding="utf-8") as f:
    f.write(f"file '{c1.resolve()}'\n")
    f.write(f"file '{c2.resolve()}'\n")
    f.write(f"file '{c3.resolve()}'\n")

print(f"[*] Concatenating scenes into {out_final}...")
cmd = [
    FFMPEG, "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", str(concat_list),
    "-c", "copy",
    str(out_final)
]
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0:
    print(f"[🎉 SUCCESS] Episode 18 Final Masterpiece Stitched: {out_final} ({out_final.stat().st_size} bytes / {out_final.stat().st_size/(1024*1024):.2f} MB)")
else:
    print("Direct concat failed, re-encoding with filter_complex...")
    cmd_reencode = [
        FFMPEG, "-y",
        "-i", str(c1),
        "-i", str(c2),
        "-i", str(c3),
        "-filter_complex", "[0:v][1:v][2:v]concat=n=3:v=1:a=0[outv]",
        "-map", "[outv]",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        str(out_final)
    ]
    res2 = subprocess.run(cmd_reencode, capture_output=True, text=True)
    if res2.returncode == 0:
        print(f"[🎉 SUCCESS] Episode 18 Re-encoded & Stitched: {out_final} ({out_final.stat().st_size} bytes / {out_final.stat().st_size/(1024*1024):.2f} MB)")
    else:
        print(f"Error stitching: {res2.stderr}")
