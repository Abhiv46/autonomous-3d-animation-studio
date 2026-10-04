import subprocess
import os
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
clip = r"C:\Users\user\Downloads\For YouTube\Children_waking_up_and_brushing_20261003082034.mp4"
out_wav = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips\test_audio1.wav"

cmd = [ffmpeg_exe, "-y", "-i", clip, "-vn", "-ar", "44100", "-ac", "2", out_wav]
subprocess.run(cmd, capture_output=True)

# Check volume level using ffmpeg volumedetect
cmd_vol = [ffmpeg_exe, "-i", out_wav, "-filter:a", "volumedetect", "-f", "null", "-"]
res = subprocess.run(cmd_vol, capture_output=True, text=True)
for line in res.stderr.splitlines():
    if "mean_volume" in line or "max_volume" in line:
        print(line.strip())
