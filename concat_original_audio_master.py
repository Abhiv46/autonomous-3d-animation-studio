import subprocess
import os
from pathlib import Path

FFMPEG = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw_clips"
OUT_DIR = DATA_DIR / "processed_episodes"
OUT_DIR.mkdir(parents=True, exist_ok=True)

s1 = RAW_DIR / "ep21_highheels_scene1_raw.mp4"
s2 = RAW_DIR / "ep21_highheels_scene2_raw.mp4"
s3 = RAW_DIR / "ep21_highheels_scene3_raw.mp4"

concat_txt = OUT_DIR / "ep21_raw_concat_list.txt"
with open(concat_txt, "w", encoding="utf-8") as f:
    f.write(f"file '{s1.resolve().as_posix()}'\n")
    f.write(f"file '{s2.resolve().as_posix()}'\n")
    f.write(f"file '{s3.resolve().as_posix()}'\n")

master_out = OUT_DIR / "TheNaughtyDuo_EP21_MummyKiHighHeels_OriginalAudio_Master.mp4"

print("Concatenating 3 raw clips with 100% ORIGINAL AUDIO and upscaling to 1080x1920 Full HD...")
cmd = [
    FFMPEG, "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", str(concat_txt),
    "-vf", "scale=1080:1920:flags=lanczos",
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "18",
    "-c:a", "aac",
    "-b:a", "192k",
    str(master_out)
]
subprocess.run(cmd, check=True)

print(f"[SUCCESS] Master video with ORIGINAL audio created:")
print(f"Path: {master_out}")
print(f"Size: {os.path.getsize(master_out)} bytes")
