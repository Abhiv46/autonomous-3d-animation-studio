import os
import shutil
import subprocess
from pathlib import Path
import imageio_ffmpeg

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
folder = r"C:\Users\user\Downloads\For Tiktok"

raw_dir = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips")
raw_dir.mkdir(parents=True, exist_ok=True)
out_dir = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output")
out_dir.mkdir(parents=True, exist_ok=True)

# List all mp4 files sorted by name/timestamp
all_files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".mp4")])
print(f"Found {len(all_files)} files in {folder}:")
copied_clips = []
for i, fname in enumerate(all_files, start=1):
    src = os.path.join(folder, fname)
    dst = raw_dir / f"tiktok_scene_{i}.mp4"
    shutil.copy2(src, dst)
    copied_clips.append(dst)
    print(f"  [{i}] {fname} -> {dst.name}")

concat_list = out_dir / "tiktok_picnic_concat.txt"
with open(concat_list, "w", encoding="utf-8") as f:
    for c in copied_clips:
        f.write(f"file '{c.as_posix()}'\n")

out_master = out_dir / "TheNaughtyDuo_TikTok_PicnicBasket_Master.mp4"

cmd = [
    ffmpeg, "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", str(concat_list),
    "-vf", "scale=1080:1920:flags=lanczos,fps=30",
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "20",
    "-c:a", "aac",
    "-b:a", "192k",
    str(out_master)
]

print("Executing FFmpeg concat & upscale to 1080x1920 30fps...")
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0:
    size_mb = out_master.stat().st_size / (1024 * 1024)
    print(f"[SUCCESS] TikTok Master Video created: {out_master}")
    print(f"Size: {size_mb:.2f} MB")
else:
    print(f"[ERROR] FFmpeg failed:\n{res.stderr}")
