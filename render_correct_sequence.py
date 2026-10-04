import os
import subprocess
from pathlib import Path
import imageio_ffmpeg

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

raw_dir = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips")
out_dir = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output")
out_dir.mkdir(parents=True, exist_ok=True)

# Exact narrative sequence requested by user:
# Part 1: Button Warning & Press ("Red button mat dabana!" -> Kaavya presses it)
# Part 2: Giant Ball Chase (Action chase scene)
# Part 3: Twist ending - Box opens and turns out to be a cute bubble machine!
s1 = raw_dir / "tiktok_ep24_scene1.mp4" # Kaavya presses red button
s2 = raw_dir / "tiktok_ep24_scene3.mp4" # Children running from giant ball
s3 = raw_dir / "tiktok_ep24_scene2.mp4" # Control box opens with bubbles (twist ending)

out_master = out_dir / "TheNaughtyDuo_TikTok_RedButtonMagic_Master_CorrectSequence.mp4"

filter_complex = (
    # Video pre-processing: scale 1080:1920 lanczos, 30fps, color enhancement
    "[0:v]scale=1080:1920:flags=lanczos,fps=30,format=yuv420p,eq=saturation=1.05:contrast=1.02,settb=AVTB[v0];"
    "[1:v]scale=1080:1920:flags=lanczos,fps=30,format=yuv420p,eq=saturation=1.05:contrast=1.02,settb=AVTB[v1];"
    "[2:v]scale=1080:1920:flags=lanczos,fps=30,format=yuv420p,eq=saturation=1.05:contrast=1.02,settb=AVTB[v2];"
    # Video cross-dissolves (0.4s dissolve at transition points)
    "[v0][v1]xfade=transition=fade:duration=0.4:offset=9.6[v01];"
    "[v01][v2]xfade=transition=fade:duration=0.4:offset=19.2[vout];"
    # Audio crossfades + fade-out at end
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

print("Rendering correct sequence: Button Press -> Giant Ball Chase -> Bubble Machine Twist Ending...")
res = subprocess.run(cmd, capture_output=True, text=True)

if res.returncode == 0:
    size_mb = out_master.stat().st_size / (1024 * 1024)
    print(f"[SUCCESS] Correct Master Video created: {out_master}")
    print(f"Size: {size_mb:.2f} MB")
else:
    print(f"[ERROR] FFmpeg failed:\n{res.stderr}")
