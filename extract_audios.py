import subprocess
import os
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
clips = [
    (1, r"C:\Users\user\Downloads\For YouTube\Children_waking_up_and_brushing_20261003082034.mp4"),
    (2, r"C:\Users\user\Downloads\For YouTube\Children_demonstrating_good_habits_20261003082503.mp4"),
    (3, r"C:\Users\user\Downloads\For YouTube\Children_washing_hands_with_soap_20261003082108.mp4"),
    (4, r"C:\Users\user\Downloads\For YouTube\Children_sharing_fruit_together_20261003082511.mp4"),
    (5, r"C:\Users\user\Downloads\For YouTube\Children_cleaning_toys_in_playroom_20261003082115.mp4"),
    (6, r"C:\Users\user\Downloads\For YouTube\Children_playing_in_park_20261003082609.mp4")
]

out_dir = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips"
for idx, path in clips:
    mp3_path = os.path.join(out_dir, f"clip_{idx}_audio.mp3")
    subprocess.run([ffmpeg_exe, "-y", "-i", path, "-vn", "-b:a", "192k", mp3_path], capture_output=True)
    print(f"Extracted clip {idx} audio: {os.path.getsize(mp3_path)} bytes")
