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

f1 = os.path.join(folder, "Children_chasing_lost_red_kite_20261003183235.mp4")
f2 = os.path.join(folder, "Children_rescuing_stuck_kite_20261003183245.mp4")
f3 = os.path.join(folder, "Family_catches_kite_together_20261003184203.mp4")

s1 = raw_dir / "kite_scene1.mp4"
s2 = raw_dir / "kite_scene2.mp4"
s3 = raw_dir / "kite_scene3.mp4"

shutil.copy2(f1, s1)
shutil.copy2(f2, s2)
shutil.copy2(f3, s3)
print("[+] Raw clips copied with clean names.")

out_master = out_dir / "TheNaughtyDuo_TikTok_KiteAdventure_Master.mp4"

# Each clip is 10.01s
# 0.4s dissolve transition at offset 9.6s and 19.2s
filter_complex = (
    "[0:v]scale=1080:1920:flags=lanczos,fps=30,format=yuv420p,eq=saturation=1.05:contrast=1.02,settb=AVTB[v0];"
    "[1:v]scale=1080:1920:flags=lanczos,fps=30,format=yuv420p,eq=saturation=1.05:contrast=1.02,settb=AVTB[v1];"
    "[2:v]scale=1080:1920:flags=lanczos,fps=30,format=yuv420p,eq=saturation=1.05:contrast=1.02,settb=AVTB[v2];"
    "[v0][v1]xfade=transition=fade:duration=0.4:offset=9.6[v01];"
    "[v01][v2]xfade=transition=fade:duration=0.4:offset=19.2[vout];"
    "[0:a][1:a]acrossfade=d=0.4:c1=tri:c2=tri[a01];"
    "[a01][2:a]acrossfade=d=0.4:c1=tri:c2=tri[a02];"
    "[a02]afade=t=in:st=0:d=0.2,afade=t=out:st=28.5:d=0.7[aout]"
)

cmd = [
    ffmpeg, "-y",
    "-i", str(s1),
    "-i", str(s2),
    "-i", str(s3),
    "-filter_complex", filter_complex,
    "-map", "[vout]",
    "-map", "[aout]",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-preset", "fast",
    "-crf", "19",
    "-c:a", "aac",
    "-b:a", "192k",
    str(out_master)
]

print("Rendering Kite Adventure Master video...")
res = subprocess.run(cmd, capture_output=True, text=True)

if res.returncode == 0:
    size_mb = out_master.stat().st_size / (1024 * 1024)
    print(f"[SUCCESS] Kite Master Video created: {out_master}")
    print(f"Size: {size_mb:.2f} MB")
else:
    print(f"[ERROR] FFmpeg failed:\n{res.stderr}")
