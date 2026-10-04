import subprocess
import os
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
clips = [
    r"C:\Users\user\Downloads\For YouTube\Children_waking_up_and_brushing_20261003082034.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_demonstrating_good_habits_20261003082503.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_washing_hands_with_soap_20261003082108.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_sharing_fruit_together_20261003082511.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_cleaning_toys_in_playroom_20261003082115.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_playing_in_park_20261003082609.mp4"
]

for i, c in enumerate(clips):
    cmd = [ffmpeg_exe, "-i", c, "-af", "volumedetect", "-vn", "-sn", "-dn", "-f", "null", "-"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    mean_v = [l for l in res.stderr.splitlines() if "mean_volume" in l]
    max_v = [l for l in res.stderr.splitlines() if "max_volume" in l]
    print(f"Clip {i+1}: {os.path.basename(c)[:30]}")
    if mean_v: print(" ", mean_v[0].strip())
    if max_v: print(" ", max_v[0].strip())
