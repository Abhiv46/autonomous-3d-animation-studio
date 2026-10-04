import subprocess
from pathlib import Path
import imageio_ffmpeg
import os

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

sequence = [
    r"C:\Users\user\Downloads\For YouTube\Children_waking_up_and_brushing_20261003082034.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_demonstrating_good_habits_20261003082503.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_washing_hands_with_soap_20261003082108.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_sharing_fruit_together_20261003082511.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_cleaning_toys_in_playroom_20261003082115.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_playing_in_park_20261003082609.mp4"
]

out_dir = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output")
out_dir.mkdir(parents=True, exist_ok=True)
master_video = out_dir / "TheNaughtyDuo_GoodHabits_Master.mp4"
music_track = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\Carefree.mp3")

# First, create concat list for the 6 clips
concat_file = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\raw_clips\good_habits_concat.txt")
with open(concat_file, "w", encoding="utf-8") as f:
    for c in sequence:
        f.write(f"file '{c}'\n")

print(f"[*] Concatenating 6 clips and mixing trending background music...")
# We concatenate video and original audio, scale to 1080:1920 lanczos, 
# and mix Carefree.mp3 looped/trimmed to 60s with subtle ducking
temp_stitched = out_dir / "temp_stitched.mp4"

# 1. Stitch video clips
cmd1 = [
    FFMPEG, "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", str(concat_file),
    "-vf", "scale=1080:1920:flags=lanczos,fps=30",
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "18",
    "-c:a", "aac",
    "-b:a", "192k",
    str(temp_stitched)
]
res1 = subprocess.run(cmd1, capture_output=True, text=True)
if res1.returncode != 0:
    print("Error in step 1:", res1.stderr)
else:
    print(f"Step 1 OK: {temp_stitched.stat().st_size} bytes")

# 2. Mix with trending background music (60s total, gentle 1.5s audio fadeout at end)
cmd2 = [
    FFMPEG, "-y",
    "-i", str(temp_stitched),
    "-i", str(music_track),
    "-filter_complex",
    "[0:a]volume=0.35[orig_a];"
    "[1:a]volume=0.85,afade=t=out:st=58.5:d=1.5[bg_a];"
    "[orig_a][bg_a]amix=inputs=2:duration=first:dropout_transition=2[out_a]",
    "-map", "0:v",
    "-map", "[out_a]",
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    str(master_video)
]
res2 = subprocess.run(cmd2, capture_output=True, text=True)
if res2.returncode == 0:
    print(f"[SUCCESS] Final Master Ready: {master_video}")
    print(f"Final Size: {master_video.stat().st_size / (1024*1024):.2f} MB")
else:
    print("Error in step 2:", res2.stderr)

# Clean up temp
if temp_stitched.exists():
    temp_stitched.unlink()
