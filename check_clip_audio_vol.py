import os
import glob
import subprocess
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
folder = r"C:\Users\user\Downloads\For YouTube"

# Test 3 clips from tonight
test_clips = [
    r"C:\Users\user\Downloads\For YouTube\Children_discovering_magical_rai._1080p_20261003210753.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_discover_glowing_red_apple_20261003211131.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_chasing_blue_butterfly_._20261003211136.mp4"
]

for clip in test_clips:
    cmd = [ffmpeg_exe, "-i", clip, "-af", "volumedetect", "-vn", "-sn", "-dn", "-f", "null", "-"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    out = res.stderr
    mean_vol = [line for line in out.split("\n") if "mean_volume" in line]
    max_vol = [line for line in out.split("\n") if "max_volume" in line]
    print(os.path.basename(clip))
    print(" ", mean_vol[0] if mean_vol else "No vol info")
    print(" ", max_vol[0] if max_vol else "No max vol")
