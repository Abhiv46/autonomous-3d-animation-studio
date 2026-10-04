import subprocess
import glob
import os
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
files = sorted(glob.glob(r"C:\Users\user\Downloads\For YouTube\*.mp4"))

for f in files:
    cmd = [ffmpeg_exe, "-i", f]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    # ffmpeg outputs stream info to stderr
    info = [line.strip() for line in res.stderr.splitlines() if "Duration" in line or "Stream" in line]
    print("FILE:", os.path.basename(f))
    for line in info:
        print("  ", line)
    print("-" * 50)
