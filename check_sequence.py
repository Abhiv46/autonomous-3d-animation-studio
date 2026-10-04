import subprocess
import glob
import os
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

sequence = [
    r"C:\Users\user\Downloads\For YouTube\Children_waking_up_and_brushing_20261003082034.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_demonstrating_good_habits_20261003082503.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_washing_hands_with_soap_20261003082108.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_sharing_fruit_together_20261003082511.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_cleaning_toys_in_playroom_20261003082115.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_playing_in_park_20261003082609.mp4"
]

print("Sequence defined:")
for idx, path in enumerate(sequence, 1):
    print(f"Scene {idx}: {os.path.basename(path)} - Exists: {os.path.exists(path)}")
