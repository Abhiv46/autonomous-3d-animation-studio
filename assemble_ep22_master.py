import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS_DIR = BASE_DIR / "data" / "raw_clips"
PROCESSED_DIR = BASE_DIR / "data" / "processed_episodes"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG_EXE = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

def stitch():
    s1 = RAW_CLIPS_DIR / "ep22_scene1.mp4"
    s2 = RAW_CLIPS_DIR / "ep22_scene2.mp4"
    s3 = RAW_CLIPS_DIR / "ep22_scene3.mp4"
    
    if not (s1.exists() and s2.exists() and s3.exists()):
        print(f"[!] Missing clips: s1={s1.exists()}, s2={s2.exists()}, s3={s3.exists()}")
        return None
        
    master_path = PROCESSED_DIR / "TheNaughtyDuo_EP22_ChocolateFaceMask_OriginalAudio_Master.mp4"
    list_path = PROCESSED_DIR / "ep22_concat_list.txt"
    
    with open(list_path, "w", encoding="utf-8") as f:
        f.write(f"file '{s1.resolve().as_posix()}'\n")
        f.write(f"file '{s2.resolve().as_posix()}'\n")
        f.write(f"file '{s3.resolve().as_posix()}'\n")
        
    print(f"[*] Stitching 1080x1920 Full HD Master with 100% Original Flow Natural Audio...")
    cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_path),
        "-vf", "scale=1080:1920:flags=lanczos",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        str(master_path)
    ]
    subprocess.run(cmd, check=True)
    print(f"[SUCCESS] Master video created: {master_path} ({os.path.getsize(master_path)} bytes)")
    return master_path

if __name__ == "__main__":
    stitch()
